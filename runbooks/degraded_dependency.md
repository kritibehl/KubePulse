# Runbook: Degraded Dependency

## Trigger

Dependency impact detected in service topology.

## Symptoms

- downstream service latency increases
- degraded-path requests rise
- p95/p99 latency drifts
- release gate blocks rollout

## Triage

1. Identify failure root in topology graph.
2. List impacted services.
3. Check whether dependency timeout or partial partition replay matches behavior.
4. Review alert summary and rollback recommendation.

## Remediation

- Isolate degraded dependency.
- Route traffic away from impacted path if possible.
- Start rollback review if candidate release caused dependency pressure.
