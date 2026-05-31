# Incident Commander Report

## Input Signal

- latency: +250%
- error rate: +8%
- CloudWatch-style alarm: ALARM
- dependency health: critical

## Decision

```json
{
  "severity": "sev1",
  "owner": "release_engineering",
  "rollback": true,
  "freeze": true,
  "customer_impact": "high"
}
Operational Meaning

KubePulse escalates severe rollout degradation into an incident-command decision with owner assignment, freeze action, rollback action, and customer-impact classification.

Safe Scope

This is a local incident-response simulation, not proof of production incident-command ownership.
