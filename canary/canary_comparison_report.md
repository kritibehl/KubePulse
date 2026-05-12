# Canary Release Comparison

Release ID: release-102

| Signal | Baseline | Candidate |
|---|---:|---:|
| p95 latency | 200.76 ms | 1422.07 ms |
| error rate | 0.01 | 0.09 |
| safe to operate | True | False |

## Decision

Rollout decision: `block`

Rollback recommended: `True`

p95 regression: 608.34%
