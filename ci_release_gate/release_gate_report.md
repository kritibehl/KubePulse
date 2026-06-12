# CI/CD Release Gate Report

## Candidate

- Release: `v1.4`
- Service: `edge-api`
- Decision: `block`
- Safe to operate: `false`

## Reason

Dependency cascade and latency drift were detected while probes remained healthy.

## Metrics

| Metric | Value |
|---|---:|
| p95 latency delta | 333.33% |
| p99 latency delta | 275.0% |
| error-rate delta | 0.08 |
| recovery window | 12s |
| probes say healthy | true |

## Gate Result

The candidate release should not proceed because system-level behavior is unsafe despite healthy readiness checks.
