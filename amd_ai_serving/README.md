# AMD AI Serving Release Gate

KubePulse includes a controlled workload-level validation layer for AMD/accelerator-backed AI-serving scenarios.

## What It Measures

- token latency
- GPU memory pressure
- GPU utilization
- throughput delta
- error-rate regression
- release decision

## Safe Scope

This is controlled workload-level validation for accelerator-backed release safety.

It does **not** claim:

- CUDA programming
- ROCm internals engineering
- GPU kernel development
- driver development
- compiler work
- production inference serving
- hardware architecture ownership

## Example Outcome

KubePulse blocks rollout when token latency rises under high GPU memory pressure.
