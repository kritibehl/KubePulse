# CI Quality Report

## CI Coverage

| Workflow | Purpose |
|---|---|
| pytest | validate Python release logic |
| release-demo | validate final release decision |
| canary-demo | validate staged rollout block |
| deployment-wave-demo | validate wave freeze logic |
| security-demo | validate policy-based release block |

## Release Criteria

A candidate is blocked when:
- SLO budget is violated
- dependency risk exceeds threshold
- CloudWatch alarm is ALARM
- security policy check fails
- rollback gate is triggered
