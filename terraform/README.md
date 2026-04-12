# KubePulse Terraform

This directory provisions a minimal AWS test environment for running KubePulse against a more production-like Kubernetes target.

## What it creates

- VPC with public and private subnets across 2 AZs
- NAT gateway
- EKS cluster
- Managed node group

## Why it exists

KubePulse detects cases where Kubernetes reports healthy while system behavior is degraded. This Terraform layer turns the project from a local-cluster demo into infrastructure-backed platform proof.

## Quick start

```bash
cd terraform
terraform init
terraform plan
Example apply
terraform apply \
  -var="aws_region=us-west-2" \
  -var="project_name=kubepulse" \
  -var="environment=dev"
Destroy
terraform destroy \
  -var="aws_region=us-west-2" \
  -var="project_name=kubepulse" \
  -var="environment=dev"

