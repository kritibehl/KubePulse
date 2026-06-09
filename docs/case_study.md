# KubePulse Case Study

## Problem
Kubernetes readiness probes can pass while user-visible health is unsafe.

## Design
KubePulse compares probe state with latency, error rate, network diagnostics, and SLO budget.

## Validation
Blocked 5 dangerous deployments with 0 false-safe decisions.

## Tradeoffs
Adds release-gate complexity, but prevents false-green rollouts.
