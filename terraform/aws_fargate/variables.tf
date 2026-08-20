variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Project prefix"
  type        = string
  default     = "kubepulse"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "demo"
}

variable "image_tag" {
  description = "ECR image tag deployed by ECS"
  type        = string
  default     = "latest"
}

variable "desired_count" {
  description = "Number of running ECS tasks"
  type        = number
  default     = 0
}
