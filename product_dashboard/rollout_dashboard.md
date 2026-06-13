# Release Safety Product Dashboard

## Summary

| Metric | Value |
|---|---:|
| Rollout count | 12 |
| Approved releases | 7 |
| Blocked releases | 4 |
| Rollback required | 1 |
| Mean time to detect | 18s |
| Median time to detect | 12s |
| Max p95 latency delta | 333.33% |
| Max p99 latency delta | 275.0% |
| Latest release decision | block |

## Incident Categories

| Category | Count |
|---|---:|
| dependency_latency | 3 |
| dns_failure | 2 |
| degraded_path | 2 |
| probe_mismatch | 4 |
| error_budget_burn | 1 |

## Why This Matters

This dashboard summarizes rollout safety as a product and operations view: how many releases were evaluated, how many were blocked, why they were blocked, and how quickly unsafe behavior was detected.
