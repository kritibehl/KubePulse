# Commissioning Sample Report

## Summary

KubePulse evaluated a containerized service under baseline and degraded network conditions.

Final decision:

```json
{
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "latency spike + probe false positive"
}
Environment
Service type: containerized API service
Validation mode: baseline vs degraded
Failure classes:
DNS failure
latency injection
degraded path
service unreachable
Scenario Results
Scenario	Probes Healthy	Safe to Operate	p95 Drift	p99 Drift	Error Delta	Recovery Window	Release Decision
degraded_path	true	false	333.33%	275.0%	0.08	12s	block
dns_failure	true	false	210.0%	240.0%	0.07	14s	block
latency_injection	true	false	333.33%	275.0%	0.08	12s	block
What Probes Missed
Downstream dependency degradation propagated upstream
Tail latency exceeded rollout budget
Service appeared healthy while user-visible behavior degraded
Recovery window exceeded safe rollout expectations
Validation Evidence

Generated artifacts:

labs/network_reliability/dns_failure_report.json
labs/network_reliability/degraded_path_report.json
labs/network_reliability/latency_injection_report.json
reports/validation_runs/validation_run_table.json
Operator Recommendation

Block rollout until:

dependency reachability is restored
p95/p99 latency returns within budget
recovery window stabilizes
probes are updated to reflect dependency availability
Result

Commissioning failed because the service remained probe-healthy while system behavior was unsafe.
