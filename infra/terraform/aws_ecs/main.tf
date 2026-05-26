terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "region" {
  default = "us-east-1"
}

variable "service_name" {
  default = "kubepulse"
}

variable "container_image" {
  description = "Container image for KubePulse"
}

provider "aws" {
  region = var.region
}

resource "aws_ecs_cluster" "kubepulse" {
  name = "${var.service_name}-cluster"
}

resource "aws_cloudwatch_log_group" "kubepulse" {
  name              = "/ecs/${var.service_name}"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "kubepulse" {
  family                   = var.service_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([
    {
      name      = var.service_name
      image     = var.container_image
      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.kubepulse.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "kubepulse"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 10
      }
    }
  ])
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.kubepulse.name
}

output "task_definition_arn" {
  value = aws_ecs_task_definition.kubepulse.arn
}
