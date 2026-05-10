# SLO Monitoring Report

KubePulse monitors release safety using threshold-based checks over latency, error rate, recovery time, and safe-to-operate signals.

## Monitored Signals

| Signal | Threshold | Purpose |
|---|---:|---|
| p95 latency | 250 ms | Detect serving or dependency regression |
| p99 latency | 500 ms | Detect tail-latency degradation |
| error rate | 2% | Detect failed request budget breach |
| recovery time | 10s | Detect slow mitigation/recovery |
| safe_to_operate | false blocks release | Detect unsafe rollout |

## Operational Outcome

When thresholds are violated, KubePulse generates an alert summary with probable cause, remediation, runbook link, and lifecycle status.
