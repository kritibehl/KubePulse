# Resilience Validation Summary

## Proof Statement

**Kubernetes resilience validation framework measuring recovery, probe integrity, and degraded-path behavior under failure.**

## Healthy vs Degraded vs Recovered

| State | Recovery Time | p50 / p95 Drift | DNS Result | Readiness Integrity | Operator Interpretation |
|---|---:|---:|---|---|---|
| Healthy | 0–5s | Minimal | DNS healthy | Probes aligned with real availability | Safe to operate |
| Degraded | Elevated / unstable | Significant drift | Partial or failed lookup / downstream impairment | False positives possible | Service may look healthy while still unsafe |
| Recovered | Returned to baseline window | Drift returns toward normal | DNS path restored | Probes realigned with dependency availability | Safe to resume normal traffic |

## What operators learn from this

- whether recovery actually completed
- whether readiness signals can be trusted
- whether degraded-path behavior still threatens correctness or availability
- whether rollout or failover is safe to continue
