output "lambda_function_name" {
    value = aws_lambda_function.incident_log_handler.function_name
}  

output "dynamodb_table_name" {
    value = aws_dynamodb_table.incidents_table.name
}