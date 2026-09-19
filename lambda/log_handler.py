import json
import os
import uuid
from datetime import datetime, timezone
import boto3

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "IncidentRecords")
table = dynamodb.Table(table_name)

logs_client = boto3.client("logs")

LOG_GROUP_NAME = "/dummy-pipeline/build-failures"
LOG_STREAM_NAME = "build-001"


def get_real_failure_log():
    """
    Pulls the most recent log events from CloudWatch.
    In the full pipeline, log group/stream would come from
    the EventBridge event payload (Task 4) - hardcoded here
    for isolated testing before that wiring exists.
    """
    response = logs_client.get_log_events(
        logGroupName=LOG_GROUP_NAME,
        logStreamName=LOG_STREAM_NAME,
        limit=20,
        startFromHead=False,
    )

    events = response.get("events", [])
    if not events:
        return "No log events found."

    log_text = "\n".join(event["message"] for event in events)
    return log_text


def build_incident_record(raw_log):
    """
    Builds a record matching the locked schema.
    ai_explanation, suggested_fix, and severity are placeholders
    for now - Rahul's Bedrock call fills these in during integration.
    """
    return {
        "incident_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "dummy-breakable-repo",
        "raw_log": raw_log,
        "ai_explanation": "",
        "suggested_fix": "",
        "severity": "unknown",
        "status": "new",
    }


def lambda_handler(event, context):
    raw_log = get_real_failure_log()
    record = build_incident_record(raw_log)

    table.put_item(Item=record)

    print(f"Incident stored: {record['incident_id']}")

    return {
        "statusCode": 200,
        "body": json.dumps({"incident_id": record["incident_id"]}),
    }