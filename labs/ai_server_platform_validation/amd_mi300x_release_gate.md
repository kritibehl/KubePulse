
AMD MI300X Release Gate
Benchmark
Baseline p95: 200.76 ms
Long-prompt burst p95: 1422.07 ms
p95 regression: +608.34%
Decision Logic
if p95_latency_delta_pct > 25:
    release_decision = block
else:
    release_decision = continue
Result
{
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "p95 latency regression under long-prompt burst load"
}

