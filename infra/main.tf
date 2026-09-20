terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- IAM Role that the Lambda function will assume ---
resource "aws_iam_role" "incident_lambda_role" {
  name = "incident-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# --- Custom policy: only what the Lambda actually needs ---
resource "aws_iam_role_policy" "incident_lambda_policy" {
  name = "incident-lambda-policy"
  role = aws_iam_role.incident_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudWatchLogsRead"
        Effect = "Allow"
        Action = [
          "logs:GetLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowDynamoDBWrite"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem"
        ]
        Resource = aws_dynamodb_table.incidents_table.arn
      },
      {
        Sid    = "AllowBedrockInvoke"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowLambdaLogging"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# --- DynamoDB Table for Incident Records ---

resource "aws_dynamodb_table" "incidents_table" {
  name = "IncidentRecords"
  billing_mode  = "PAY_PER_REQUEST"
  hash_key = "incident_id"

  attribute {
    name = "incident_id"
    type = "S"
  }

  tags = {
    Project = "incident-command-center"
  }
}

# --- Lambda Function ---

resource "aws_lambda_function" "incident_log_handler" {
  function_name = "incident-log-handler"
  role = aws_iam_role.incident_lambda_role.arn
  handler = "log_handler.lambda_handler"
  runtime = "python3.12"
  filename = "${path.module}/../lambda/function.zip"
   source_code_hash = filebase64sha256("${path.module}/../lambda/function.zip")
  timeout = 15

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.incidents_table.name
    }
  }   
}

resource "aws_iam_user" "rahul" {
  name = "rahul-bhagwat"
}

resource "aws_iam_user_policy_attachment" "rahul_bedrock" {
  user       = aws_iam_user.rahul.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}

resource "aws_iam_user" "prapti" {
  name = "prapti-sharma"
}

resource "aws_iam_user_policy_attachment" "prapti_amplify" {
  user       = aws_iam_user.prapti.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmplifyBackendDeployFullAccess"
}

resource "aws_iam_access_key" "rahul_key" {
  user = aws_iam_user.rahul.name
}

resource "aws_iam_access_key" "prapti_key" {
  user = aws_iam_user.prapti.name
}

resource "aws_iam_user_policy" "prapti_dynamodb_read" {
  name = "prapti-dynamodb-read"
  user = aws_iam_user.prapti.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.incidents_table.arn
      }
    ]
  })
}

resource "aws_iam_user" "github_actions" {
  name = "github-actions-trigger"
}

resource "aws_iam_user_policy" "github_actions_eventbridge" {
  name = "github-actions-eventbridge-put"
  user = aws_iam_user.github_actions.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = "*"
      }
    ]
  })
  
}

resource "aws_iam_access_key" "github_actions_key" {
  user = aws_iam_user.github_actions.name
}

resource "aws_cloudwatch_event_rule" "build_failure_rule" {
  name = "catch-build-failures"
  description = "Triggers incident lambda when a build failure event arrives"
  
  event_pattern = jsonencode({
    "source" : ["dummy.pipeline"],
    "detail-type": ["BuildFailed"]
  })
}

resource "aws_cloudwatch_event_target" "invoke_lambda" {
  rule = aws_cloudwatch_event_rule.build_failure_rule.name
  target_id = "incident-lambda-target"
  arn = aws_lambda_function.incident_log_handler.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id = "AllowEventBridgeinvoke"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.incident_log_handler.function_name
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.build_failure_rule.arn
}

resource "aws_iam_role" "eb_instance_role" {
  name = "eb-incident-api-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eb_web_tier" {
  role       = aws_iam_role.eb_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

resource "aws_iam_role_policy" "eb_dynamodb_read" {
  name = "eb-dynamodb-read"
  role = aws_iam_role.eb_instance_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.incidents_table.arn
      }
    ]
  })
}

resource "aws_iam_instance_profile" "eb_instance_profile" {
  name = "eb-incident-api-instance-profile"
  role = aws_iam_role.eb_instance_role.name
}