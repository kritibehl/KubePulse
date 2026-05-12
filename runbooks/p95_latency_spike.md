# Runbook: p95 Latency Spike

## Trigger

`kubepulse_latency_p95_ms > 250`

## Symptoms

- p95 latency exceeds release budget
- canary candidate performs worse than baseline
- alert may fire while readiness probe remains healthy

## Triage

1. Compare baseline vs candidate p95.
2. Check whether error rate also increased.
3. Inspect impacted dependency path.
4. Review release decision artifact.
5. Check whether rollback recommendation exists.

## Remediation

- Block rollout if latency regression exceeds threshold.
- Start rollback review.
- Re-run canary comparison after mitigation.
