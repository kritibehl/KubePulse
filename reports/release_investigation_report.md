
# KubePulse Release Investigation Report

## Release

Release ID: release-102

## Timeline

- Deployment start: 2026-04-21T16:00:00Z
- Latency regression detected: 2026-04-21T16:03:12Z
- Error-rate increase detected: 2026-04-21T16:04:02Z
- Release blocked: 2026-04-21T16:05:10Z
- Rollback review started: 2026-04-21T16:06:00Z

## Correlated Signals

- p95 latency regression: 608.34%
- Error-rate increase: 8.0%
- Probe healthy: True
- Safe to operate: False

## Suspected Root Cause

long_prompt_burst_resource_saturation

## Rollback Recommendation

Rollback recommended: True

Reasons:
- p95_latency_budget_violation
- probe_mismatch_false_green
- error_rate_budget_violation

Recommended action:
rollback_candidate_release
