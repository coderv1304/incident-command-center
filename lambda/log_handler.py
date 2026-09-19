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
    In a fuller production version, the log group/stream would
    also come from the EventBridge event payload rather than
    being hardcoded - kept fixed here since this hackathon's
    dummy pipeline always writes to the same log group/stream.
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
 
 
def build_incident_record(raw_log, source="dummy-breakable-repo"):
    """
    Builds a record matching the locked schema.
    ai_explanation and suggested_fix are placeholders here until
    Rahul's Bedrock integration fills them in as part of this
    same Lambda's execution (or a follow-up call).
    """
    return {
        "incident_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "raw_log": raw_log,
        "ai_explanation": "",
        "suggested_fix": "",
        "severity": "unknown",
        "status": "new",
    }
 
 
def lambda_handler(event, context):
    """
    Entry point. Triggered either manually (via the Lambda console
    test, with an empty {} event) or automatically by EventBridge
    (with a real event payload carrying the repository and run ID
    from the dummy pipeline's GitHub Actions failure).
    """
    detail = event.get("detail", {})
    repository = detail.get("repository", "unknown-repo")
 
    raw_log = get_real_failure_log()
    record = build_incident_record(raw_log, source=repository)
 
    table.put_item(Item=record)
 
    print(f"Incident stored: {record['incident_id']}")
 
    return {
        "statusCode": 200,
        "body": json.dumps({"incident_id": record["incident_id"]}),
    }
 
