output "lambda_function_name" {
    value = aws_lambda_function.incident_log_handler.function_name
}  

output "dynamodb_table_name" {
    value = aws_dynamodb_table.incidents_table.name
}

output "rahul_access_key_id" {
    value = aws_iam_access_key.rahul_key.id
}

output "rahul_secret_access_key" {
    value = aws_iam_access_key.rahul_key.secret
    sensitive = true
}

output "prapti_access_key_id" {
    value = aws_iam_access_key.prapti_key.id
}

output "prapti_secret_access_key" {
    value = aws_iam_access_key.prapti_key.secret
    sensitive = true
}