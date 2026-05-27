# SQS-Style Deployment Event Flow

## Event Types

- deployment_started
- canary_validation_failed
- cloudwatch_alarm_triggered
- rollback_gate_triggered
- deployment_wave_frozen
- release_recovered

## Queue Semantics

The queue buffers rollout events so the release evaluator can process deployment state transitions in order.

## Example Event

```json
{
  "event_type": "cloudwatch_alarm_triggered",
  "deployment_id": "deploy-204",
  "alarm": "HighLatencyAlarm",
  "state": "ALARM"
}
Retention Notes
Keep release-block artifacts for audit review.
Keep rollback evidence for post-incident analysis.
Keep summarized metrics for trend analysis.
Safe Scope

This is an S3-style artifact plan, not a live S3 bucket deployment.
