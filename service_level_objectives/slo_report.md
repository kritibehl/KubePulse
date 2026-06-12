# SLO Report

## Service

`edge-api`

## Objective

Validate whether the service remains within rollout safety and reliability targets during baseline and degraded scenarios.

## SLO Summary

```json
{
  "availability": 99.92,
  "error_budget_remaining": 63,
  "release_decision": "block"
}
Reliability Targets
Objective	Target	Observed	Status
Availability	99.95%	99.92%	warning
p95 latency	<= 300ms	780ms	violated
p99 latency	<= 900ms	1200ms	violated
Error rate	<= 1%	8%	violated
Recovery window	<= 10s	12s	violated
Decision

block

Reason

The service violated latency, error-rate, and recovery-window objectives while Kubernetes readiness remained healthy.

What Probes Missed
Downstream latency propagation
Tail-latency violation
Error-budget burn
Recovery instability
