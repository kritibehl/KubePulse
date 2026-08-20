# KubePulse AWS Fargate Demo

This Terraform stack provisions the AWS runtime foundation for the KubePulse release-safety demo.

Resources:

- Amazon ECR repository
- Amazon ECS Fargate cluster/service
- ECS execution/task IAM roles
- CloudWatch log group
- Security group
- Existing default VPC/subnets

The service initially deploys with `desired_count=0` so infrastructure can be provisioned before the first container image is pushed.
