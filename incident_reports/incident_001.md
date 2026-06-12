# Incident Report: INC-001

## Summary

KubePulse detected an unsafe rollout condition for `edge-api` caused by dependency latency propagation.

## Impact

- Service: `edge-api`
- Severity: high
- Impact: unsafe rollout prevented
- Release decision: `block`
- Safe to operate: `false`

## Metrics

| Metric | Value |
|---|---:|
| p95 latency delta | 333.33% |
| p99 latency delta | 275.0% |
| error-rate delta | 0.08 |
| recovery window | 12s |

## Timeline

| Time | Event |
|---|---|
| T+0s | candidate release validation started |
| T+2s | dependency latency propagated upstream |
| T+5s | p95 and p99 latency exceeded rollout budget |
| T+8s | probe mismatch detected |
| T+12s | release decision set to block |

## Root Cause

Dependency latency propagated through the service path while Kubernetes readiness checks remained healthy.

## Mitigation

- Block rollout.
- Investigate downstream dependency latency.
- Tighten readiness checks to include dependency availability.
- Re-run validation before deployment.

## Lessons Learned

Readiness probes are insufficient for release safety when dependency latency and tail latency drift are not evaluated.
