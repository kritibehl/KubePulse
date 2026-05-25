# HPA Autoscaling Scenario

## Scenario

A candidate rollout increases request latency and CPU pressure during release validation.

## HPA Policy

| Setting | Value |
|---|---:|
| min replicas | 1 |
| max replicas | 5 |
| target CPU | 70% |

## Release-Safety Interpretation

Autoscaling may add capacity, but KubePulse still blocks rollout if SLOs remain violated.

## Decision Rule

If latency/error budgets are violated after autoscaling pressure is detected:

`release_decision=block`

## Safe Scope

This is an autoscaling validation artifact, not proof of production Kubernetes autoscaling ownership.
