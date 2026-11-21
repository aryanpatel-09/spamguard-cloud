variable "aws_region" {
  description = "AWS region for deploying SpamGuard resources"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix for all AWS resources"
  type        = string
  default     = "spamguard-api"
}
