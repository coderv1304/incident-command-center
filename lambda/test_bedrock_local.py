#!/usr/bin/env python3
"""
Test harness for Amazon Bedrock AI Incident Analysis
Can run in mock mode (default) or live mode against AWS Bedrock.
"""

import argparse
import json
import sys
from bedrock_service import analyze_log_with_bedrock, _clean_and_parse_json

SAMPLE_LOGS = {
    "npm_dependency_conflict": (
        "npm ERR! code ERESOLVE\n"
        "npm ERR! ERESOLVE could not resolve\n"
        "npm ERR! While resolving: react-router-dom@7.0.0\n"
        "npm ERR! Found: react@17.0.2\n"
        "npm ERR! Could not resolve dependency:\n"
        "npm ERR! peer react@\"^18.0.0\" from react-router-dom@7.0.0"
    ),
    "docker_auth_failure": (
        "Step 4/10 : FROM 123456789012.dkr.ecr.ap-south-1.amazonaws.com/app:latest\n"
        "docker: Error response from daemon: pull access denied for app, repository does not exist or may require 'docker login': denied: Your authorization token has expired."
    ),
    "python_type_error": (
        "Traceback (most recent call last):\n"
        "  File \"app/main.py\", line 42, in process_event\n"
        "    user_id = payload['user']['id']\n"
        "TypeError: 'NoneType' object is not subscriptable"
    ),
    "missing_env_var": (
        "Starting incident API service on port 8080...\n"
        "FATAL: Missing required environment variable DATABASE_URL. Application cannot connect to database and will now exit."
    )
}

def run_test(live=False):
    print("=" * 70)
    print(f"Running Bedrock AI Log Analysis Verification (Mode: {'LIVE AWS' if live else 'MOCK / FALLBACK'})")
    print("=" * 70)

    for sample_name, log_text in SAMPLE_LOGS.items():
        print(f"\n--- Testing Sample: [{sample_name}] ---")
        print("Raw Log Input:")
        for line in log_text.splitlines()[:3]:
            print(f"  | {line}")
        if len(log_text.splitlines()) > 3:
            print("  | ... (truncated)")

        result = analyze_log_with_bedrock(log_text)

        print("\nAI Layer Output:")
        print(json.dumps(result, indent=2))

        # Schema validations
        assert "ai_explanation" in result, "Missing ai_explanation"
        assert "suggested_fix" in result, "Missing suggested_fix"
        assert "severity" in result, "Missing severity"
        assert result["severity"] in ["HIGH", "MEDIUM", "LOW"], f"Invalid severity: {result['severity']}"
        print(f"✅ Schema Validation Passed for [{sample_name}]")

    print("\n" + "=" * 70)
    print("All tests passed successfully! Contract intact.")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Bedrock AI Layer")
    parser.add_argument("--live", action="store_true", help="Invoke live Amazon Bedrock API using active AWS credentials")
    args = parser.parse_args()
    run_test(live=args.live)

