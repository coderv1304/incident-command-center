# Incident Command Center

**AI Incident & Anomaly Command Center** — an event-driven AWS pipeline that detects CI/CD pipeline failures automatically, generates a plain-English root-cause explanation using Amazon Bedrock, and displays it on a live dashboard.

Built for **First Commit** (Bharat Builds Tour, Sept 17–20, 2026) by **Team Code&Chill**.

---

## Team

| Name | Role |
|---|---|
| Varun Nair | AWS / DevOps / Infrastructure (Team Leader) |
| Rahul Bhagwat | AI Layer (Amazon Bedrock) |
| Prapti Sharma | Backend (Spring Boot) & Frontend (React) |

---

## Architecture

```
Dummy breakable GitHub repo
        │  (real failure via GitHub Actions)
        ▼
Amazon EventBridge (detects the failure automatically)
        │
        ▼
AWS Lambda (Python) — pulls real failure logs from CloudWatch
        │
        ▼
Amazon Bedrock (Claude) — root cause + fix  [integration in progress]
        │
        ▼
Amazon DynamoDB — stores the full incident record
        │
        ▼
Spring Boot API → React Dashboard → AWS Amplify Hosting
```

---

## Progress Log

### Day 1 — Thursday, Sept 17

**Infrastructure and Lambda setup completed by Varun:**

- ✅ Repository, branches, and team contracts locked (DynamoDB schema, Bedrock response shape, API response shape)
- ✅ IAM role and least-privilege policy defined and deployed via Terraform (`incident-lambda-execution-role`)
- ✅ DynamoDB table (`IncidentRecords`) deployed via Terraform
- ✅ Lambda function (`incident-log-handler`) written and deployed via Terraform
- ✅ End-to-end manual test completed successfully — Lambda executed, generated a real incident record, and wrote it correctly to DynamoDB

**Verification — record written correctly, matching the locked schema:**
```json
{
  "incident_id": "6d02e9fb-cb82-49d6-89c2-0793d4f164c4",
  "raw_log": "hardcoded sample failure log",
  "severity": "unknown",
  "status": "new",
  "source": "dummy-breakable-repo",
  "ai_explanation": "",
  "suggested_fix": ""
}
```

**Status:** Varun's Day 1 infrastructure and Lambda setup is fully complete and verified working end-to-end, independently of the AI and frontend layers.

---

**Backend & Frontend setup completed by Prapti:**

- ✅ Spring Boot REST API scaffolded (`com.codechill.incidentapi`) with an `Incident` model matching the locked contract
- ✅ `IncidentController` exposes `GET /api/incidents` returning sample incident records
- ✅ CORS configured via `@CrossOrigin(origins = "http://localhost:3000")` for local React dev
- ✅ React dashboard scaffolded with live incident feed, AI explanation panel, severity color-coding, and expandable raw-log viewer
- ✅ Axios integrated in React to consume the Spring Boot API
- ✅ Frontend → Backend integration verified locally — dashboard renders incident cards with AI explanations and severity badges
- ✅ Both API (port 8081) and Dashboard (port 3000) running concurrently for end-to-end local demo

**Verification — Spring Boot API response (mock data):**
```json
GET http://localhost:8081/api/incidents
[
  {
    "incident_id": "INC-001",
    "timestamp": "2026-09-17T10:30:00",
    "source": "github-actions",
    "raw_log": "Error: Cannot find module 'express'",
    "ai_explanation": "The build failed because the 'express' package is missing. Run 'npm install express' and try again.",
    "severity": "HIGH",
    "status": "OPEN"
  }
]
```

> **Known issue to resolve before the real DynamoDB swap:** the mock data above uses `severity` values like `"HIGH"`/`"MEDIUM"` and a `status` of `"OPEN"`, while the locked schema (and Varun's actual deployed data) uses lowercase `severity` (e.g. `"unknown"`) and `status: "new"`/`"acknowledged"`. The dashboard's severity color-coding needs to be normalized to match the real casing/values before connecting to live data, or badges may fail to render correctly.

**Status:** Prapti's Day 1 backend + frontend stack is fully complete and verified working end-to-end with mock data, independently of Varun's Lambda/DynamoDB and Rahul's Bedrock integration.

---

### Day 2 — Friday, Sept 18

**Scoped access and real log integration — Varun**

- ✅ Created scoped IAM users for Rahul (Bedrock access) and Prapti (Amplify + DynamoDB read access), each with their own access keys — least-privilege, no shared root credentials
- ✅ Replaced the hardcoded test log with real CloudWatch log retrieval: Lambda now pulls actual log events from a dedicated CloudWatch log group (`/dummy-pipeline/build-failures`) via `boto3`
- ✅ Added DynamoDB read-only permissions for Prapti's Spring Boot integration, and documented the connection details (table name, region, schema) for her to build against
- ✅ Verified end-to-end: a real CloudWatch log event flows through the Lambda and lands correctly in DynamoDB with the real log text, not a placeholder

**Notable debugging:** recovered from an accidental deletion of the IAM users (caused by running `terraform apply` from a branch with an out-of-date `main.tf`) — rebuilt and reverified without any impact to the core pipeline.

**Status:** Real log ingestion pipeline fully working and verified.

**Backend/Frontend — Prapti:** *(update once confirmed)* swap from mock data to real DynamoDB reads — pending confirmation.

---

### Day 3 — Saturday, Sept 19

**Automatic end-to-end trigger — Varun**

- ✅ Added a failure-notification step to the dummy repo's GitHub Actions workflow, using a dedicated least-privilege IAM identity (`github-actions-trigger`, scoped to `events:PutEvents` only) to push a real event into EventBridge whenever the pipeline fails
- ✅ Created the EventBridge rule and target wiring the failure event directly to the Lambda function, including the required Lambda resource policy permitting EventBridge to invoke it
- ✅ Updated the Lambda to read the real event payload (repository name, run ID) dynamically from EventBridge, rather than using a hardcoded value
- ✅ **Full end-to-end test verified live:** a real commit pushed to the dummy repo triggered a real pipeline failure, which automatically fired an EventBridge event, which triggered the Lambda, which pulled the real CloudWatch log and wrote a complete record to DynamoDB — correct repository name, correct log content, zero manual steps anywhere in the chain

**Notable debugging:** resolved a Terraform resource-type mismatch (`aws_iam_user_policy_attachment` vs `aws_iam_user_policy`, and `aws_cloudwatch_event_permission` vs `aws_lambda_permission`), a missing `source_code_hash` argument that was silently preventing Lambda code updates from deploying, and a malformed JSON payload in the GitHub Actions workflow.

**Status: core automatic pipeline is fully complete.** Every piece — detection, log retrieval, storage — works end-to-end without manual intervention. The only remaining piece is Rahul's Bedrock integration, which will populate the `ai_explanation` and `suggested_fix` fields once merged in.

**Frontend — Prapti:** *(update once confirmed)* Amplify Hosting deployment — pending confirmation.

---

## Tech Stack

**Infrastructure (Varun):** AWS IAM, Terraform, AWS Lambda (Python), Amazon EventBridge, Amazon CloudWatch Logs, Amazon DynamoDB, GitHub Actions

**AI (Rahul):** Amazon Bedrock (Claude), Python

**Backend/Frontend (Prapti):** Java Spring Boot, React, AWS Amplify Hosting

---

## AI Tools Used

- GitHub Copilot
