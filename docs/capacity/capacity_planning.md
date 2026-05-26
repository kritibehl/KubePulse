# Capacity Planning Notes

KubePulse uses load-test and autoscaling artifacts to evaluate release readiness.

## Capacity Signals

- p95 latency
- p99 latency
- error rate
- peak concurrent users
- autoscaling threshold
- release decision

## Release Readiness Rule

A candidate release is not ready if:

- p95 latency exceeds budget
- p99 latency exceeds budget
- error rate exceeds budget
- autoscaling pressure appears but SLOs remain violated

## Operational Outcome

When capacity thresholds are exceeded, KubePulse recommends:

- block rollout
- inspect bottleneck
- review autoscaling thresholds
- rerun load validation after remediation

## Safe Scope

This is a simulated capacity-validation workflow, not proof of production load testing.
