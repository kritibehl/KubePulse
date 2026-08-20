output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "region" {
  value = var.aws_region
}

output "ecr_repository_name" {
  value = aws_ecr_repository.app.name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app.name
}

output "task_definition_arn" {
  value = aws_ecs_task_definition.app.arn
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.app.name
}

output "security_group_id" {
  value = aws_security_group.app.id
}

output "subnet_ids" {
  value = data.aws_subnets.default.ids
}
