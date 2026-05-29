# Resource Pressure Summary

## Signals

| Signal | Current Value | Risk |
|---|---:|---|
| p95 latency | 640 ms | high |
| p99 latency | 910 ms | high |
| error rate | 4% | high |
| replicas | 3 | watch |
| CPU limit | 500m | constrained |
| memory limit | 512Mi | constrained |

## Release Safety

KubePulse blocks or delays rollout continuation when resource pressure causes latency or error-budget risk.

## Recommended Actions

- increase replica count before high-traffic rollout
- monitor p95/p99 during canary expansion
- review HPA thresholds
- rerun capacity validation after scaling
