# Service Health Dashboard Summary

## Service: edge-api

| Signal | Value |
|---|---:|
| p95 latency drift | 333.33% |
| p99 latency drift | 275.0% |
| error-rate delta | 0.08 |
| recovery window | 12s |
| degraded path requests | 37 |
| probes say healthy | true |
| safe to operate | false |
| release decision | block |

## Dashboard Interpretation

The service appears healthy at the probe level, but runtime behavior is unsafe for rollout.

## Alerts Triggered

- p95 latency drift
- p99 tail latency drift
- probe mismatch
- dependency degradation
