# KubePulse Network Lab: Baseline vs Degraded Experiments

## Experiment 1: DNS Failure

| Metric | Baseline | Degraded |
|---|---:|---:|
| Request success | 25/25 | 0/25 |
| Request failure | 0/25 | 25/25 |
| p50 latency | 5.259 ms | 6.731 ms |
| p95 latency | 12.691 ms | 10.216 ms |

**Interpretation:** disconnecting the downstream auth dependency from the service network caused complete end-to-end request failure across the dependency chain.

## Experiment 2: API Path Latency Injection

| Metric | Baseline | Degraded |
|---|---:|---:|
| Request success | 25/25 | 23/25 |
| Request failure | 0/25 | 2/25 |
| p50 latency | 4.888 ms | 1.462 s |
| p95 latency | 10.120 ms | 2.306 s |

**Interpretation:** injecting delay and packet loss on the API hop caused major end-to-end latency inflation and partial request failure.

## Topology

`edge -> api-service -> auth-service`

## Failure Types Exercised

- DNS failure
- latency / packet loss injection
- partial service partition
- intermittent connection churn
