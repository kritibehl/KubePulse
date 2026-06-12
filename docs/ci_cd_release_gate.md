# CI/CD Release Gate

KubePulse converts resilience-validation results into deployment decisions.

## Decisions

- `continue`: rollout can proceed
- `hold`: rollout requires review
- `block`: rollout should stop

## Gate Inputs

- `safe_to_operate`
- `release_decision`
- p95 latency delta
- p99 latency delta
- error-rate delta
- recovery window
- probe mismatch status
- dependency health

## Example Gate Output

```json
{
  "candidate_release": "v1.4",
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "dependency cascade + latency drift",
  "p95_latency_delta_pct": 333.33,
  "error_rate_delta": 0.08
}
CI/CD Usage

A deployment pipeline can run KubePulse before rollout and fail the pipeline when release_decision=block.

Why This Matters

Container health checks can stay green while service behavior becomes unsafe. KubePulse gates releases on runtime behavior, not just pod status.
