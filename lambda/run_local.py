#!/usr/bin/env python3
"""
Interactive Local Runner for Incident Command Center (AI Layer)

Usage:
  python run_local.py
  python run_local.py --sample docker
  python run_local.py --live
"""

import argparse
import json
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bedrock_service import analyze_log_with_bedrock
from log_handler import build_incident_record, get_sample_failure_log
from anomaly_detector import calculate_z_score_anomaly

SAMPLES = {
    "npm": (
        "ERROR: npm install failed\n"
        "Reason: Could not resolve dependency 'react-router-dom@7.0.0'\n"
        "peer react@\"^18.0.0\" from react-router-dom@7.0.0\n"
        "Found: react@17.0.2\n"
        "Fix the version mismatch and re-run the pipeline."
    ),
    "docker": (
        "Step 4/10 : FROM 123456789012.dkr.ecr.ap-south-1.amazonaws.com/app:latest\n"
        "docker: Error response from daemon: pull access denied for app: "
        "denied: Your authorization token has expired. Run 'aws ecr get-login-password' to refresh."
    ),
    "python": (
        "Traceback (most recent call last):\n"
        "  File \"app/main.py\", line 42, in process_event\n"
        "    user_id = payload['user']['id']\n"
        "TypeError: 'NoneType' object is not subscriptable"
    ),
    "database": (
        "FATAL: Connection to PostgreSQL failed at localhost:5432\n"
        "Error: Missing required environment variable DATABASE_URL. "
        "Application cannot establish connection pool and is shutting down."
    )
}

def main():
    parser = argparse.ArgumentParser(description="Local runner for AI Incident Analysis")
    parser.add_argument("--sample", choices=list(SAMPLES.keys()), default="npm",
                        help="Choose sample failure log to analyze (default: npm)")
    parser.add_argument("--live", action="store_true",
                        help="Invoke live Amazon Bedrock API (requires AWS credentials)")
    parser.add_argument("--custom-log", type=str, default=None,
                        help="Pass a custom error log string to analyze")
    args = parser.parse_args()

    print("=" * 75)
    print("  🚨 INCIDENT COMMAND CENTER — LOCAL AI LAYER EXECUTION 🚨")
    print("=" * 75)

    if args.custom_log:
        raw_log = args.custom_log
        sample_name = "Custom Log Input"
    else:
        sample_name = args.sample
        raw_log = SAMPLES.get(sample_name, get_sample_failure_log())

    print(f"\n[1] Selected Failure Log ({sample_name}):")
    print("-" * 75)
    print(raw_log.strip())
    print("-" * 75)

    # If live mode requested, inform user of Bedrock model & region
    if args.live:
        region = os.environ.get("BEDROCK_REGION", os.environ.get("AWS_REGION", "ap-south-1"))
        model = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
        print(f"\n[2] Connecting to Amazon Bedrock...")
        print(f"    Region   : {region}")
        print(f"    Model ID : {model}")
    else:
        print("\n[2] Analyzing with AI Layer (Local / Heuristic fallback mode)...")
        print("    (Tip: Pass --live when your AWS credentials are configured)")

    # Execute build_incident_record (the actual Lambda logic)
    incident = build_incident_record(raw_log, source="local-test-repo")

    print("\n[3] Generated DynamoDB Incident Record:")
    print("-" * 75)
    print(json.dumps(incident, indent=2))
    print("-" * 75)

    # Execute Stretch Goal: Statistical Anomaly Detection
    print("\n[4] Running Statistical Anomaly Check (Stretch Goal):")
    # Simulate historical failure counts per hour for this pipeline: [1, 2, 1, 1, 2] vs sudden surge of 6 failures
    historical_failures = [1, 2, 1, 1, 2]
    current_failures = 6
    anomaly_result = calculate_z_score_anomaly(historical_failures, current_failures)

    print(f"    Historical Failure Baseline (per hr) : {historical_failures}")
    print(f"    Current Failure Count (last hr)      : {current_failures}")
    print(f"    Z-Score                              : {anomaly_result['z_score']}")
    print(f"    Is Anomaly Detected?                 : {'⚠️  YES - SPIKE DETECTED!' if anomaly_result['is_anomaly'] else '✅ NO - Normal'}")
    print(f"    Message                              : {anomaly_result['message']}")

    print("\n" + "=" * 75)
    print("  ✅ EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 75)

if __name__ == "__main__":
    main()

