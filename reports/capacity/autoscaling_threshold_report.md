# Autoscaling Threshold Report

## Scenario

KubePulse evaluated release readiness under simulated load.

## HPA Policy

| Signal | Threshold |
|---|---:|
| CPU utilization | 70% |
| min replicas | 1 |
| max replicas | 5 |
| p95 latency budget | 250 ms |
| p99 latency budget | 500 ms |
| error-rate budget | 2% |

## Observed Load Result

| Metric | Observed | Budget | Status |
|---|---:|---:|---|
| p95 latency | 620 ms | 250 ms | fail |
| p99 latency | 910 ms | 500 ms | fail |
| error rate | 5% | 2% | fail |
| peak VUs | 50 | n/a | observed |

## Decision

`release_decision=block`

## Interpretation

Autoscaling may be recommended, but release continuation remains blocked because latency and error-rate budgets were violated under simulated load.
