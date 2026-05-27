# Weekly Operational Review

## Summary

KubePulse tracks release-health signals for cloud rollout review.

## Weekly Signals

| Signal | Value | Status |
|---|---:|---|
| deployments reviewed | 6 | observed |
| releases blocked | 2 | actioned |
| rollback reviews | 2 | actioned |
| SLA breaches | 1 | review required |
| error-budget burn | 80% | high risk |

## Key Risks

- high p95 latency during canary validation
- CloudWatch-style alarm entered ALARM
- dependency-risk score exceeded release threshold
- rollback gate triggered for degraded site

## Decision

Continue staged rollout only after rollback review and dependency-health recovery.
