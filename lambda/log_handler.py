import json
import os
import uuid
import boto3
from datetime import datetime, timezone
from bedrock_service import analyze_log_with_bedrock


dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'IncidentRecords')
table = dynamodb.Table(table_name)

def get_sample_failure_log():
    """
    Stand-in for real CloudWatch log retrieval.
    Replace this with an actual boto3 CloudWatch Logs call
    once this piece is confirmed working end-to-end.
    """
    return (
        "ERROR: npm install failed\n"
        "Reason: Could not resolve dependency 'react-router-dom@7.0.0'\n"
        "peer react@\"^18.0.0\" from react-router-dom@7.0.0\n"
        "Found: react@17.0.2\n"
        "Fix the version mismatch and re-run the pipeline."
    )

def build_incident_record(raw_log, source="dummy-breakable-repo"):
    """
    Builds a record matching the locked schema.
    ai_explanation, suggested_fix, and severity are generated via Amazon Bedrock Claude.
    """
    ai_analysis = analyze_log_with_bedrock(raw_log)

    return {
        "incident_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "raw_log": raw_log,
        "ai_explanation": ai_analysis.get("ai_explanation", "Pipeline failure detected."),
        "suggested_fix": ai_analysis.get("suggested_fix", "Check build configuration."),
        "severity": ai_analysis.get("severity", "MEDIUM"),
        "status": "OPEN"
    }

def lambda_handler(event, context):
    # Support direct raw_log invocation or fallback to sample log
    raw_log = None
    source = "dummy-breakable-repo"

    if isinstance(event, dict):
        raw_log = event.get("raw_log")
        source = event.get("source", source)

    if not raw_log:
        raw_log = get_sample_failure_log()

    record = build_incident_record(raw_log, source=source)
    table.put_item(Item=record)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "incident_id": record["incident_id"],
            "severity": record["severity"],
            "ai_explanation": record["ai_explanation"]
        }),
    }