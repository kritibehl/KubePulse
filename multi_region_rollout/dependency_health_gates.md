# Dependency Health Gates

## Purpose

Dependency-health gates prevent rollout continuation when upstream or downstream services are degraded.

## Checked Signals

| Signal | Gate |
|---|---|
| dependency risk score | block if > 80 |
| packet loss | block if above threshold |
| p95 latency | block if above budget |
| p99 latency | block if above budget |
| error rate | block if above budget |
| critical downstream service | freeze next wave if unhealthy |

## Example

Critical path:

`edge-gateway -> checkout -> payments`

If `payments` is critical or degraded, KubePulse blocks rollout continuation and triggers rollback review.

## Release Decision

Dependency health gates feed into:

- `safe_to_operate`
- `release_decision`
- `freeze_next_wave`
- `rollback_required`
