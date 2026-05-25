# Terraform + CloudWatch Notes

KubePulse can be extended with Terraform-managed CloudWatch alarms for release-safety signals.

## Example Resources To Add

- `aws_cloudwatch_metric_alarm` for unsafe release
- `aws_cloudwatch_metric_alarm` for p95 latency
- `aws_cloudwatch_metric_alarm` for error-rate budget
- `aws_sns_topic` for alert routing

## Example Alarm Logic

```hcl
resource "aws_cloudwatch_metric_alarm" "unsafe_release" {
  alarm_name          = "kubepulse-unsafe-release"
  comparison_operator = "LessThanThreshold"
  threshold           = 1
  evaluation_periods  = 1
  metric_name         = "SafeToOperate"
  namespace           = "KubePulse"
  period              = 60
  statistic           = "Minimum"
}
Safe Scope

This documents Terraform/CloudWatch integration design. It does not claim production AWS monitoring ownership.
