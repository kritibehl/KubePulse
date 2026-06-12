# Burn Rate Alerts

## Purpose

Burn-rate alerts identify when a service is consuming reliability budget faster than expected.

## Alert Inputs

- availability
- error-rate delta
- p95 latency drift
- p99 latency drift
- recovery window
- dependency health
- probe mismatch

## Example Alert

```json
{
  "service": "edge-api",
  "availability": 99.92,
  "error_budget_remaining": 63,
  "burn_rate_status": "elevated",
  "release_decision": "block"
}
Alert Levels
Level	Condition	Action
normal	budget stable	continue
elevated	budget burn increasing	hold
critical	budget burn + unsafe behavior	block
Example Critical Conditions
p95 latency drift > 100%
p99 latency drift > 100%
error-rate delta > 0.02
recovery window > target
probe mismatch detected
Operator Action
Hold or block rollout.
Review dependency health.
Check p95/p99 latency drift.
Confirm error-budget remaining.
Re-run KubePulse validation after mitigation.
