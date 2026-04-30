# Validation Data Schema

KubePulse exports scenario validation runs as reproducible JSON artifacts.

## Purpose

The validation data layer captures whether a system is safe to deploy under degraded-but-healthy conditions.

It tracks:

- scenario name
- failure class
- probe state
- rollout decision
- p95 / p99 latency drift
- error-rate delta
- recovery window
- degraded-path evidence
- reason for release decision

## Canonical decision fields

```json
{
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "latency spike + probe false positive"
}
Validation run table fields
Field	Meaning
scenario	Scenario name, such as dns_failure or degraded_path
failure_class	Type of failure being simulated
probes_say_healthy	Whether probes remained green
safe_to_operate	Whether system behavior is safe enough for rollout
release_decision	continue, hold, reroute, or block
reason	Human-readable decision reason
latency_p95_drift_pct	p95 latency drift from baseline
latency_p99_drift_pct	p99 latency drift from baseline
error_rate_delta	Error-rate increase from baseline
recovery_window_seconds	Time until recovery or stabilization
source_artifact	Original scenario JSON artifact
Example
{
  "scenario": "degraded_path",
  "failure_class": "degraded_network_route",
  "probes_say_healthy": true,
  "safe_to_operate": false,
  "release_decision": "block",
  "latency_p95_drift_pct": 333.33,
  "latency_p99_drift_pct": 275.0,
  "error_rate_delta": 0.08,
  "recovery_window_seconds": 12
}

