# KubePulse Incident Response Runbook

## Purpose

Use this runbook when KubePulse detects unsafe release conditions, SLO violations, or false-green probe behavior.

## Triage Steps

1. Check whether `safe_to_operate=false`.
2. Identify violated thresholds: p95 latency, p99 latency, error rate, recovery time, or probe mismatch.
3. Confirm whether readiness probes stayed healthy.
4. Review release-decision artifact.
5. Start rollback review if release decision is `block`.

## Remediation

- Roll back candidate release if latency/error budgets are violated.
- Isolate degraded dependency if failure is dependency-related.
- Re-run replay scenario after mitigation.
- Confirm metrics return below configured thresholds.

## Audit / Compliance Notes

- Keep alert summary artifact.
- Record acknowledgement status.
- Preserve runbook link and remediation status.
