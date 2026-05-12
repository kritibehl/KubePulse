# SLO Burn-Rate Analysis

## Summary

KubePulse evaluates release risk using latency, error-rate, availability, and recovery-time budgets.

## Observed Release Risk

| Signal | Budget | Observed | Status |
|---|---:|---:|---|
| Availability | 99.9% | 99.2% | budget risk |
| p95 latency | 250 ms | 1422.07 ms | violated |
| Error rate | 2% | 9% | violated |
| Recovery time | 10s | 12s | violated |

## Burn-Rate Interpretation

The candidate rollout burns error budget too quickly and violates latency/recovery thresholds.

## Release Gate

Decision: `block`

## Rollback Threshold

Rollback review is required because multiple reliability budgets were violated during release validation.
