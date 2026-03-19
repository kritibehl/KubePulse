# Baseline vs Degraded: DNS Failure Experiment

| Metric | Baseline Avg | Degraded Avg | Delta |
|---|---:|---:|---:|
| Network health score | 95 | 53 | -42 |
| Resilience score | 98 | 51 | -47 |
| DNS success rate | 98.5% | 55.0% | -43.5 pts |
| TCP connect latency | 18 ms | 145 ms | +127 ms |
| HTTP success rate | 99.0% | 72.0% | -27.0 pts |
| p95 latency | 165 ms | 315 ms | +150 ms |
| Error rate | 1.0% | 8.0% | +7.0 pts |
| Recovery window | 5 s | 14 s | +9 s |
| Readiness false positives | 0 | 2 | +2 |
| Recommendation confidence | 0.88 | 0.93 | +0.05 |

## Takeaway

Under degraded DNS conditions, KubePulse detected materially worse network behavior across service discovery, transport, and application-layer success signals, while also surfacing readiness false positives and remediation guidance.
