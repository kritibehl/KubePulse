# Manual-to-Automated Test Conversion

## Manual Review

Historically, release reviewers inspect rollout signals manually:
- p95/p99 latency
- error rate
- CloudWatch alarm state
- dependency health
- rollback recommendation

## Automated Conversion

KubePulse converts these checks into repeatable validation scripts:
- `make release-demo`
- `make canary-demo`
- `make deployment-wave-demo`
- `make security-demo`
- `make capacity-demo`

## Benefit

The same release-risk checks can be repeated in CI and reviewed as structured artifacts.
