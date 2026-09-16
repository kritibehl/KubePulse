# AI Serving Platform Validation Lab (AMD MI300X)

This lab validates whether an AI serving system is actually ready for production.

It checks Linux host health, ROCm/vLLM readiness, endpoint connectivity, latency regression, and release safety on AMD MI300X.

## Stack

- Hardware: AMD MI300X
- Runtime: ROCm
- Serving: vLLM
- Model: microsoft/Phi-3-mini-4k-instruct

## Architecture

```text
Prompt load → vLLM on AMD MI300X → latency benchmark → KubePulse gate → block/continue decision
Result
Metric	Value
Baseline p95	200.76 ms
Long-prompt burst p95	1422.07 ms
p95 regression	+608.34%
safe_to_operate	false
release_decision	block
Release Decision
{
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "p95 latency regression under long-prompt burst load"
}
Resume Value

Validated AI serving release gates on AMD MI300X using ROCm/vLLM; blocked rollout after +608% p95 latency regression under long-prompt burst load.
