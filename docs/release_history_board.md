# Release History Board

KubePulse tracks release-readiness outcomes across validation runs.

## Purpose

The release history board captures:

- approved releases
- blocked releases
- rollback-required deployments
- regression reason
- impacted service
- p95 / p99 latency delta
- error-rate delta
- release-readiness decision

## Example Summary

```json
{
  "approved_releases": 1,
  "blocked_releases": 1,
  "rollback_required": 1
}
Example Release Record
{
  "release_id": "rel-2026-04-001",
  "service": "edge-api",
  "decision": "blocked",
  "rollback_required": false,
  "reason": "dependency cascade + latency drift",
  "p95_latency_delta_pct": 333.33,
  "p99_latency_delta_pct": 275.0,
  "error_rate_delta": 0.08,
  "release_readiness": "unsafe"
}
Why This Matters

Single validation runs are useful, but release systems need historical readiness evidence.

KubePulse uses release history to show whether deployments were approved, blocked, or marked rollback-required based on measurable runtime degradation.
