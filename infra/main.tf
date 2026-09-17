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
  timeout = 15

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.incidents_table.name
    }
  }   
}
