# AMD AI Serving Release Report

## Summary

KubePulse evaluates accelerator-backed AI-serving release safety using controlled workload-level signals.

## Signals

| Signal | Value |
|---|---:|
| GPU memory pressure | 88% |
| Token latency | 1422 ms |
| Throughput delta | -18% |
| Error rate | 5% |
| Release decision | block |

## Decision

`release_decision=block`

## Why

High GPU memory pressure correlated with token-latency regression and error-rate budget violation.

## Artifacts

- `amd_ai_serving/screenshots/token_latency_vs_memory_pressure.png`
- `amd_ai_serving/screenshots/amd_release_decision_block.png`

## Safe Scope

This is controlled workload-level validation for accelerator-backed release safety. It does not claim CUDA/kernel work, ROCm internals, driver development, compiler work, or production inference serving.
