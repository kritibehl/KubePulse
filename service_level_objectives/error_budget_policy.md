# Error Budget Policy

## Purpose

KubePulse uses error budget signals to determine whether a service is safe to release.

## Policy

A rollout should be blocked when:

- `safe_to_operate=false`
- p95 or p99 latency exceeds rollout budget
- error-rate delta exceeds allowed threshold
- recovery window exceeds target
- dependency degradation burns reliability budget
- probes remain healthy while system behavior is unsafe

## Example Budget State

```json
{
  "availability": 99.92,
  "error_budget_remaining": 63
}
Decision Rules
Condition	Action
Error budget remaining > 75% and no latency regression	continue
Error budget remaining between 50% and 75% with mild regression	hold
Error budget remaining < 50%	block
Probe mismatch detected with unsafe behavior	block
Dependency cascade detected	block
KubePulse Mapping
Signal	Release Impact
p95 latency drift	indicates user-facing degradation
p99 latency drift	indicates tail-latency risk
error-rate delta	consumes error budget
recovery window	indicates operational stability
safe_to_operate	final safety state
release_decision	rollout action
