# Commissioning Test Plan

This plan describes how KubePulse can be used to validate a containerized service before rollout or environment handoff.

## Goal

Confirm that a service is safe to operate under expected and degraded conditions before release.

## Commissioning Stages

### 1. Environment Readiness

Validate:

- service starts successfully
- container health endpoint responds
- dependency endpoints are configured
- network routes are reachable
- DNS resolves expected service names

Example checks:

```bash
curl -v http://<service>/health
nslookup <dependency-service>
nc -vz <dependency-host> <port>
2. Baseline Run

Capture normal operating behavior.

Metrics:

p50 latency
p95 latency
p99 latency
error rate
recovery window
dependency reachability

Expected decision:

{
  "safe_to_operate": true,
  "release_decision": "continue"
}
3. Degraded Run

Run KubePulse scenarios under controlled degradation:

DNS failure
latency injection
degraded network path
partial partition
service unreachable
retry storm

Expected behavior:

probes may remain healthy
system may become unsafe
release decision should reflect observed degradation
4. Regression Comparison

Compare baseline and candidate/degraded runs.

Review:

p95 drift
p99 drift
error-rate delta
recovery window
degraded-path requests
release decision

Example regression output:

{
  "latency_p95_delta_pct": 200.0,
  "latency_p99_delta_pct": 175.0,
  "error_budget_delta": 0.03,
  "regression_verdict": "regressed"
}
5. Rollout Decision

Use the canonical KubePulse decision fields:

{
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "latency spike + probe false positive"
}
Pass / Fail Criteria
Check	Pass	Fail
Health endpoint	responds	unavailable
DNS	resolves expected target	fails or resolves incorrectly
Connectivity	reachable target port	timeout / refused
p95 latency	within budget	drift exceeds threshold
p99 latency	within budget	tail latency spike
Error rate	within budget	exceeds error budget
Recovery	within window	unstable or delayed
Release decision	continue / hold	block
Artifacts

Each commissioning run should produce:

scenario output JSON
validation run table
release decision
latency visualization
notes on probe mismatch or dependency failure
Example Command Flow
python cli/kubepulse.py run
python cli/kubepulse.py compare
python pipelines/export_validation_runs.py
Outcome

Commissioning succeeds only if the service remains safe under baseline behavior and expected degradation classes.
