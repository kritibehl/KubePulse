# Hardware Validation Report

## Purpose

KubePulse includes a hardware-adjacent release gate for accelerator-backed or hardware-sensitive workloads.

## Signals Reviewed

| Signal | Value |
|---|---:|
| device visible | true |
| driver/runtime ready | true |
| GPU utilization | 92% |
| memory pressure | 88% |
| temperature | 81 C |
| p95 latency | 1422 ms |
| throughput delta | -18% |
| error rate | 5% |

## Release Decision

`block`

## Reason

KubePulse blocked release continuation because memory pressure, GPU saturation, latency regression, and error-rate budget violations indicated unsafe hardware-backed rollout behavior.

## Safe Scope

This is a hardware-adjacent validation workflow. It does not claim GPU kernel development, ROCm internals, driver work, compiler work, or production inference serving.
