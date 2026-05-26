# Horizontal Scaling Comparison

| Replicas | Queue Depth | p95 ms | p99 ms | Error Rate | Status |
|---:|---:|---:|---:|---:|---|
| 1 | 180 | 1422.07 | 1880.4 | 0.09 | fail |
| 3 | 64 | 640.5 | 910.2 | 0.04 | watch |
| 5 | 12 | 238.7 | 412.3 | 0.01 | pass |

Autoscaling recovery time: `46s`

Release decision: `block_until_recovered`

Reason: release remains blocked until p95/p99 latency and queue depth recover below threshold