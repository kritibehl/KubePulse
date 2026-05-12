# Release Failure Recovery Sequence

## Incident

Incident ID: `kubepulse-release-102`

## Sequence

1. Candidate release started.
2. SLO breach detected when p95 latency exceeded the release budget.
3. Alert fired for unsafe release and high p95 latency.
4. Rollback recommendation engine classified the incident as `sev1`.
5. Rollback was recommended for the candidate release.
6. Service recovered after rollback review and metrics returned below threshold.

## Operational Signals

| Signal | Value |
|---|---:|
| Baseline p95 | 200.76 ms |
| Candidate p95 | 1422.07 ms |
| p95 regression | 608.34% |
| Release decision | block |
| Severity | sev1 |
| Status | remediated |

## Recovery Workflow

detected -> alerted -> rollback_recommended -> rollback_review -> remediated

## Why This Matters

This timeline reconstructs the operational sequence from deployment start to recovery, making the incident easier to explain during release reviews, SRE handoffs, and post-incident analysis.
