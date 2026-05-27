# SLA Breach Summary

## Breach

Candidate rollout exceeded latency and error-rate budgets.

| Metric | Budget | Observed |
|---|---:|---:|
| p95 latency | 250 ms | 620 ms |
| p99 latency | 500 ms | 910 ms |
| error rate | 2% | 5% |

## Operational Impact

- release decision: `block`
- rollback required: `true`
- next deployment wave frozen: `true`

## Remediation

- rollback candidate release
- reroute degraded dependency path
- rerun release validation after recovery
