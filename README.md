# Incident Command Center

**AI Incident & Anomaly Command Center** — an event-driven AWS pipeline that detects CI/CD pipeline failures automatically, generates a plain-English root-cause explanation using Amazon Bedrock, and displays it on a live dashboard.

Built for **First Commit** (Bharat Builds Tour, Sept 17–20, 2026) by **Team Code&Chill**.

**Live demo:** https://main.d375eel1bwxyyg.amplifyapp.com

---

## Team

| Name | Role |
|---|---|
| Varun Nair | AWS / DevOps / Infrastructure (Team Leader) |
| Rahul Bhagwat | AI Layer (Amazon Bedrock) |
| Prapti Sharma | Backend (Spring Boot) & Frontend (React) |

---

## The Problem

When a CI/CD pipeline fails, an engineer has to manually open logs, read through raw error text, and figure out what broke and why — a repetitive task that typically takes 20-40 minutes per incident, repeated identically across every team, every failure, with no memory of past diagnoses.

## The Solution

An automated pipeline that detects a failure the instant it happens, retrieves the real failure logs, generates a plain-English explanation of the root cause, stores a permanent record, and displays it on a live dashboard — with zero manual steps from detection to display.

---

## How the Whole System Works, End to End

This is the complete path a single failure takes through the system, in the order it actually happens:

### 1. A real failure occurs
A dummy GitHub repository has a GitHub Actions workflow (`build.yml`) that intentionally fails one step (`exit 1`), simulating a real broken build or deployment.

### 2. GitHub Actions notifies AWS
Because GitHub Actions runs entirely outside AWS, it has no built-in way to tell AWS a failure happened. A second workflow step, which only runs `if: failure()`, uses the AWS CLI to send a custom event into **Amazon EventBridge**, carrying the real repository name and run ID. This step authenticates using a dedicated, narrowly-scoped IAM identity (`github-actions-trigger`) that can do exactly one thing: `events:PutEvents` — nothing else. This is the bridge between a non-AWS system and AWS's event infrastructure.

### 3. EventBridge catches the event and triggers the Lambda
An **EventBridge rule** is configured to watch for exactly this event shape (`source: "dummy.pipeline"`, `detail-type: "BuildFailed"`). The instant a matching event arrives, EventBridge automatically invokes the project's **AWS Lambda** function — no polling, no scheduled check, genuinely event-driven. A separate **Lambda resource policy** explicitly grants EventBridge permission to invoke the function (Lambda denies invocation from other services by default; without this permission the whole chain would silently do nothing).

### 4. The Lambda retrieves the real failure log
The Lambda function (Python) reads the event payload to get the real repository name, then calls **Amazon CloudWatch Logs** via `boto3` to pull the actual failure log text from a dedicated log group. This is the same mechanism a real AWS-native pipeline (like CodeBuild) would use natively; here it's built explicitly since GitHub Actions doesn't log into CloudWatch on its own.

### 5. The Lambda calls Bedrock for an explanation
The raw log text is sent to **Amazon Bedrock**, which runs a Claude model prompted specifically to act as a build-failure analyst. Bedrock returns a structured response: a plain-English root cause, a suggested fix, and a severity rating. *(This integration is in progress — see Progress Log below for current status.)*

### 6. The complete record is written to DynamoDB
The Lambda assembles everything — the log, the AI explanation, the severity, a timestamp, the real source repository — into a single record and writes it to **Amazon DynamoDB** (`IncidentRecords` table). This is the permanent, queryable history of every incident the system has ever seen; nothing is lost to a chat scrollback or a terminal that got closed.

### 7. The backend serves this data over the internet
A **Spring Boot REST API**, deployed on **AWS Elastic Beanstalk**, reads directly from DynamoDB using its own dedicated IAM instance role (scoped to read-only: `GetItem`, `Query`, `Scan` — the running application authenticates as itself, not as a person). This turns the raw database table into a clean `GET /api/incidents` endpoint any frontend can consume.

### 8. CloudFront bridges HTTP to HTTPS
Elastic Beanstalk serves plain HTTP by default. The dashboard, once deployed, is served over HTTPS — and browsers block an HTTPS page from calling an HTTP endpoint directly (a "mixed content" security restriction). **Amazon CloudFront** sits in front of the Elastic Beanstalk backend specifically to solve this: it accepts HTTPS requests from the dashboard and forwards them to the backend over HTTP, giving the whole system a secure, browser-trusted path without needing to configure SSL certificates directly on Elastic Beanstalk.

### 9. The dashboard displays it live
The **React dashboard**, deployed on **AWS Amplify Hosting**, calls the API (through CloudFront) and renders every incident as a card — showing the failure, the AI's explanation, severity, and a collapsible raw log viewer. Amplify Hosting builds and redeploys this dashboard automatically every time new code is pushed to the `main` branch on GitHub.

**The result:** a failure that happens on GitHub, with zero manual intervention anywhere, ends up visible on a public, live URL within seconds — detected, logged, explained, and displayed, entirely automatically.

---

## Every AWS Service Used, and Exactly Why

| Service | What it does here | Why this service specifically |
|---|---|---|
| **Amazon EventBridge** | Watches for the custom "build failed" event and automatically triggers the Lambda | Native event-driven trigger — no polling, no scheduled Lambda checking for failures, reacts instantly when something happens |
| **AWS Lambda** | Runs the Python orchestration logic: reads the event, fetches the log, calls Bedrock, writes to DynamoDB | Serverless — scales to zero when idle, no server to manage or pay for between failures, which suits this bursty, unpredictable workload |
| **Amazon CloudWatch Logs** | Stores the raw failure log text the Lambda retrieves | The standard AWS-native logging destination; used here to simulate what a real CI/CD pipeline's logs would look like inside AWS |
| **Amazon Bedrock** | Runs the Claude model that turns a raw log into a plain-English explanation | Managed foundation model access — no model hosting, no GPU infrastructure to provision, just an API call |
| **Amazon DynamoDB** | Permanent storage for every incident record | Serverless, on-demand billing (`PAY_PER_REQUEST`) — fits an unpredictable read/write pattern without provisioning fixed capacity; simple key-based access matches the data shape exactly |
| **AWS Elastic Beanstalk** | Hosts the Spring Boot backend on real AWS compute | The simplest way to deploy a standard Java web application to AWS — handles the underlying EC2 instance and environment without needing to manage servers by hand |
| **Amazon CloudFront** | Sits in front of Elastic Beanstalk, converts HTTPS requests to HTTP for the origin | Solves a real, concrete problem: the HTTPS dashboard cannot call an HTTP-only backend directly due to browser security restrictions; CloudFront provides HTTPS termination without needing a certificate configured directly on Elastic Beanstalk |
| **AWS Amplify Hosting** | Builds and hosts the React dashboard, connected directly to GitHub | Automatic build-and-deploy on every push to `main`; gives the frontend a real, public HTTPS URL in minutes, which is the literal definition of the event's "Ship It" track |
| **AWS IAM** | Every identity in the system — the Lambda's role, each teammate's user, the Elastic Beanstalk instance role, the GitHub Actions identity | Enforces least-privilege throughout: no shared root credentials in any running code, every identity can do exactly what it needs and nothing more |
| **Terraform** | Defines and deploys the IAM roles, DynamoDB table, Lambda function, EventBridge rule, and Elastic Beanstalk instance role as code | No manual console click-ops for the core infrastructure — every resource is reproducible and reviewable as a `.tf` file, which is also what the event's judging criteria explicitly checks for |

---

## Progress Log

### Day 1 — Thursday, Sept 17

**Infrastructure and Lambda foundation — Varun**

- Repository, branches, and team contracts locked (DynamoDB schema, Bedrock response shape, API response shape)
- IAM role and least-privilege policy deployed via Terraform (`incident-lambda-execution-role`)
- DynamoDB table (`IncidentRecords`) deployed via Terraform
- Lambda function (`incident-log-handler`) written and deployed via Terraform
- End-to-end manual test completed successfully

**Backend & Frontend setup — Prapti**

- Spring Boot REST API scaffolded with an `Incident` model matching the locked contract
- `IncidentController` exposing `GET /api/incidents`
- React dashboard scaffolded with live incident feed, AI explanation panel, severity color-coding, and expandable raw-log viewer
- Frontend → backend integration verified locally with mock data

---

### Day 2 — Friday, Sept 18

**Scoped access and real log integration — Varun**

- Created scoped IAM users for Rahul (Bedrock access) and Prapti (Amplify + DynamoDB read access)
- Replaced the hardcoded test log with real CloudWatch log retrieval via `boto3`
- Documented DynamoDB connection details for Prapti's backend integration

**Notable debugging:** recovered from an accidental IAM user deletion caused by applying Terraform from a branch with an out-of-date `main.tf` — rebuilt cleanly and reinforced a stricter plan-before-apply discipline for the rest of the build.

**Backend/Frontend — Prapti**

- Spring Boot API connected to real DynamoDB, replacing mock data
- React dashboard confirmed rendering live, real incident records

---

### Day 3 — Saturday, Sept 19

**Automatic end-to-end trigger — Varun**

- Added a failure-notification step to the dummy repo's GitHub Actions workflow, using a dedicated least-privilege IAM identity to push a real event into EventBridge on failure
- Created the EventBridge rule, target, and Lambda resource permission wiring the failure event directly to the Lambda
- Updated the Lambda to read the real event payload (repository name, run ID) dynamically
- **Full end-to-end test verified live:** a real GitHub Actions failure automatically triggered EventBridge → Lambda → CloudWatch log retrieval → a complete, correctly-populated DynamoDB record — zero manual steps

**Notable debugging:** resolved two Terraform resource-type mismatches (`aws_iam_user_policy_attachment` vs `aws_iam_user_policy`; `aws_cloudwatch_event_permission` vs `aws_lambda_permission`), a missing `source_code_hash` argument silently blocking Lambda code updates, and a malformed JSON payload in the GitHub Actions workflow.

**Full deployment — Frontend, Backend, and connecting them — Varun & Prapti**

- React dashboard deployed to **AWS Amplify Hosting**, resolving a monorepo build-path issue (`appRoot`) and an out-of-sync `package-lock.json`
- Spring Boot backend deployed to **AWS Elastic Beanstalk**, with a dedicated IAM instance role granting least-privilege DynamoDB read access
- Diagnosed a browser "Mixed Content" block preventing the HTTPS frontend from calling the HTTP-only backend directly
- Deployed **Amazon CloudFront** in front of Elastic Beanstalk as an HTTPS bridge; resolved a follow-on origin protocol misconfiguration (HTTPS-only vs HTTP-only) causing a 504 timeout
- **Full end-to-end system verified live:** the public Amplify dashboard successfully fetches real incident data through CloudFront → Elastic Beanstalk → DynamoDB, confirmed via direct testing and browser network inspection, zero mock data or localhost dependencies remaining

**Status: the entire pipeline — detection, log retrieval, storage, backend, and live public dashboard — is fully deployed on real AWS infrastructure and verified working end-to-end.** The one remaining piece is Rahul's Bedrock integration, which will populate the `ai_explanation` and `suggested_fix` fields on new incidents; every other part of the system, including the plumbing to receive and display that data, is already built, deployed, and tested.

---

## Tech Stack

**Infrastructure (Varun):** AWS IAM, Terraform, AWS Lambda (Python), Amazon EventBridge, Amazon CloudWatch Logs, Amazon DynamoDB, AWS Elastic Beanstalk, Amazon CloudFront, GitHub Actions

**AI (Rahul):** Amazon Bedrock (Claude), Python

**Backend/Frontend (Prapti):** Java Spring Boot, React, AWS Amplify Hosting

---

## AI Tools Used

- GitHub Copilot - for fixing some parentheses errors
- Claude 3.5(Sonnet)
