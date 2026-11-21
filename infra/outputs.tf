output "lambda_function_url" {
  description = "Public HTTPS endpoint for the SpamGuard Lambda API"
  value       = aws_lambda_function_url.spam_detector_url.function_url
}

output "lambda_function_name" {
  description = "Deployed AWS Lambda function name"
  value       = aws_lambda_function.spam_detector.function_name
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group name"
  value       = aws_cloudwatch_log_group.lambda_log_group.name
}
