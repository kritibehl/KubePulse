# CloudWatch Metrics Mapping

KubePulse Prometheus-style signals can be mapped into CloudWatch-style metrics.

| KubePulse Signal | CloudWatch Metric Name | Purpose |
|---|---|---|
| `kubepulse_safe_to_operate` | `SafeToOperate` | Release safety state |
| `kubepulse_latency_p95_ms` | `LatencyP95Ms` | p95 latency budget |
| `kubepulse_latency_p99_ms` | `LatencyP99Ms` | p99 latency budget |
| `kubepulse_error_rate` | `ErrorRate` | Error budget |
| `kubepulse_release_block_total` | `ReleaseBlockTotal` | Release-block count |

## Alert Examples

- `SafeToOperate == 0`
- `LatencyP95Ms > 250`
- `ErrorRate > 0.02`
- `ReleaseBlockTotal > 0`

## Safe Scope

This is a CloudWatch-compatible mapping/design note, not a live AWS CloudWatch deployment.
