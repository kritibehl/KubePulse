# Canary-to-Global Rollout

## Rollout Sequence

1. Start canary wave at one site.
2. Validate DNS/TCP/TLS and container health.
3. Check p95/p99 latency and error budget.
4. Evaluate CloudWatch-style alarm state.
5. Evaluate dependency-health gates.
6. Run release decision engine.
7. Continue only when `safe_to_operate=true`.
8. Freeze or rollback when release decision is `block`.

## Example Block

KubePulse blocked rollout when:

- p95 latency exceeded budget
- error rate exceeded budget
- CloudWatch-style alarm entered `ALARM`
- dependency risk score exceeded threshold
- rollback gate triggered
