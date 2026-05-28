# End-to-End Test Plan

## Scope

Validate KubePulse release-safety workflows from deployment input through release decision output.

## Test Areas

| Area | What To Validate |
|---|---|
| Release gate | unsafe deployments are blocked |
| Canary rollout | watch → hold → block transitions |
| Deployment waves | failed wave freezes next wave |
| Network validation | degraded dependency path blocks release |
| Security validation | missing TLS/auth/resources blocks release |
| Capacity validation | p95/p99 and error-rate violations block release |

## Edge Cases

- readiness probe healthy but SLO unsafe
- CloudWatch-style alarm is ALARM
- dependency risk score exceeds threshold
- rollback gate triggered
- missing resource limits
- insecure env vars
