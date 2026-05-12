# Runbook: Release Block Response

## Trigger

`release_decision=block`

## Immediate Actions

1. Acknowledge alert.
2. Confirm `safe_to_operate=false`.
3. Review blocked rollout reasons.
4. Check rollback recommendation.
5. Notify service owner or platform on-call based on severity.

## Decision Criteria

Rollback review is required when:
- p95 latency budget is violated
- error-rate budget is violated
- alert is firing
- dependency impact is detected
- candidate is not safe to operate

## Closure

Close only after:
- metrics return below threshold
- release decision changes to continue
- incident summary is attached
