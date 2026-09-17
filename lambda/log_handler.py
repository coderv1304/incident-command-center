import json
import os
import uuid
import boto3
from datetime import datetime, timezone


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

def build_incident_record(raw_log):
    """
    Builds a record matching the locked schema.
    ai_explanation, suggested_fix, and severity are placeholders
    for now — Rahul's Bedrock call fills these in during integration.
    """
    return {
        "incident_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "dummy-breakable-repo",
        "raw_log": raw_log,
        "ai_explanation": "",
        "suggested_fix": "",
        "severity": "unknown",
        "status": "new"
    }

def lambda_handler(event, context):
    raw_log = get_sample_failure_log()
    record = build_incident_record(raw_log)
    table.put_item(Item=record)

    return {
        "statusCode": 200,
        "body": json.dumps({"incident_id": record["incident_id"]}),
    }