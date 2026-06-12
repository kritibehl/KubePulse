# Monitoring and Alerting Policy

KubePulse alerting converts degradation signals into rollout-safety alerts.

## Alert Classes

| Alert | Severity | Trigger |
|---|---|---|
| p95 latency drift | warning / critical | p95 exceeds rollout budget |
| p99 latency drift | warning / critical | tail latency exceeds budget |
| error-rate increase | warning / critical | error budget delta exceeds threshold |
| dependency unreachable | critical | service dependency cannot be reached |
| DNS failure | critical | dependency name cannot resolve |
| probe mismatch | critical | probes healthy but safe_to_operate=false |

## Example Critical Alert

```json
{
  "alert": "probe_mismatch",
  "severity": "critical",
  "service": "edge-api",
  "release_decision": "block"
}
Operator Response
Hold or block rollout.
Check dependency reachability.
Review p95/p99 latency drift.
Confirm recovery window.
Update readiness checks if probes missed dependency failure.
