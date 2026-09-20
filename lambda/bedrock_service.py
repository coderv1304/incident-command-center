import json
import logging
import os
import re
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configuration with environment variable overrides
DEFAULT_REGION = os.environ.get("AWS_REGION", "ap-south-1")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", DEFAULT_REGION)
# Claude 3 Haiku is ideal for fast, cost-effective CI/CD log triage
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

SYSTEM_PROMPT = """You are an expert DevOps and Site Reliability Engineer analyzing CI/CD pipeline failure logs.
Your task is to analyze the provided raw log snippet and diagnose the root cause with maximum clarity and actionable solutions.

You MUST respond strictly with a valid JSON object containing exactly these keys:
{
  "ai_explanation": "A clear, concise, plain-English explanation (2-3 sentences) of what failed and why.",
  "suggested_fix": "Concrete, step-by-step commands or actions the developer should take to resolve the error.",
  "severity": "HIGH | MEDIUM | LOW"
}

Severity classification guidelines:
- HIGH: Build/deployment breaking errors, missing critical dependencies, database connection failures, authentication/permission denied.
- MEDIUM: Test suite failures, configuration warnings treated as errors, transient timeouts.
- LOW: Minor linting/formatting issues, non-blocking deprecations.

Output only valid JSON. Do not include markdown code fences or conversational text outside the JSON object.
"""

def _get_bedrock_client():
    """Initializes and returns the boto3 Bedrock Runtime client."""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=BEDROCK_REGION
    )

def _clean_and_parse_json(response_text: str) -> dict:
    """Safely extracts and parses JSON from the model response."""
    text = response_text.strip()
    
    # Strip markdown code fences if model wrapped response in ```json ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
        
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "ai_explanation" in data and "severity" in data:
            return data
    except json.JSONDecodeError:
        # Attempt regex fallback to find innermost JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
                
    raise ValueError(f"Could not parse valid incident JSON from model response: {response_text[:100]}")

def _heuristic_fallback(raw_log: str, error_context: str = "") -> dict:
    """
    Fallback analyzer in case Bedrock is temporarily unavailable or times out.
    Ensures the Lambda pipeline never drops an incident record.
    """
    log_lower = raw_log.lower()
    
    if any(k in log_lower for k in ["syntaxerror", "cannot find module", "could not resolve dependency", "fatal"]):
        severity = "HIGH"
    elif any(k in log_lower for k in ["failed", "error", "typeerror", "exception"]):
        severity = "MEDIUM"
    else:
        severity = "LOW"
        
    explanation = "Automated pipeline failure detected. "
    if "cannot find module" in log_lower or "could not resolve dependency" in log_lower:
        explanation += "A required package or dependency is missing or has a version conflict."
        suggested_fix = "Review your dependency lockfile (package.json / requirements.txt) and reinstall packages."
    elif "syntaxerror" in log_lower or "typeerror" in log_lower:
        explanation += "A code-level exception or type mismatch was encountered during execution."
        suggested_fix = "Inspect the stack trace in the raw log and fix the offending code line."
    else:
        explanation += "The build or deployment step exited with a non-zero exit code."
        suggested_fix = "Examine the raw log details below to identify the failing command."

    if error_context:
        explanation += f" (Note: Bedrock inference fallback applied: {error_context})"

    return {
        "ai_explanation": explanation,
        "suggested_fix": suggested_fix,
        "severity": severity
    }

def analyze_log_with_bedrock(raw_log: str) -> dict:
    """
    Analyzes a raw CI/CD failure log using Amazon Bedrock (Claude).
    
    Returns a dictionary conforming to the locked team contract:
    {
        "ai_explanation": str,
        "suggested_fix": str,
        "severity": str  # "HIGH", "MEDIUM", or "LOW"
    }
    """
    if not raw_log or not raw_log.strip():
        return {
            "ai_explanation": "No failure log provided for analysis.",
            "suggested_fix": "Verify that CI/CD log streaming is sending output to CloudWatch.",
            "severity": "LOW"
        }

    user_prompt = f"Analyze the following CI/CD pipeline failure log:\n\n```\n{raw_log}\n```"

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 600,
        "temperature": 0.1,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    try:
        client = _get_bedrock_client()
        logger.info("Invoking Bedrock model %s in %s...", BEDROCK_MODEL_ID, BEDROCK_REGION)
        
        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        response_body = json.loads(response.get("body").read().decode("utf-8"))
        
        # Claude 3 response format: response_body["content"][0]["text"]
        model_output_text = ""
        content_blocks = response_body.get("content", [])
        for block in content_blocks:
            if block.get("type") == "text":
                model_output_text += block.get("text", "")

        parsed_result = _clean_and_parse_json(model_output_text)
        
        # Normalize severity
        sev = str(parsed_result.get("severity", "MEDIUM")).upper()
        if sev not in ["HIGH", "MEDIUM", "LOW"]:
            sev = "MEDIUM"
        parsed_result["severity"] = sev

        # Ensure all required keys exist
        parsed_result.setdefault("ai_explanation", "Pipeline failure analyzed.")
        parsed_result.setdefault("suggested_fix", "Inspect the raw log for details.")

        return parsed_result

    except (ClientError, BotoCoreError) as aws_err:
        logger.warning("Bedrock API call failed: %s. Using heuristic fallback.", str(aws_err))
        return _heuristic_fallback(raw_log, error_context=f"Bedrock API error: {aws_err.response.get('Error', {}).get('Code', 'AWSException') if hasattr(aws_err, 'response') else 'ClientError'}")
    except Exception as exc:
        logger.error("Unexpected error in Bedrock log analysis: %s", str(exc), exc_info=True)
        return _heuristic_fallback(raw_log, error_context="General processing error")

