# Incident Response Workflow

KubePulse incident reports capture service impact, root cause, mitigation, recovery timeline, and release decision.

## Workflow

1. Run release validation.
2. Detect unsafe behavior.
3. Capture metrics and impacted service.
4. Generate incident report.
5. Recommend rollout action.
6. Re-run validation after mitigation.

## Incident Fields

- incident ID
- service impacted
- severity
- root cause
- p95 / p99 latency delta
- error-rate delta
- recovery window
- release decision
- mitigation steps

## Example Decision

```json
{
  "service": "edge-api",
  "severity": "high",
  "root_cause": "dependency latency propagation",
  "release_decision": "block"
}
