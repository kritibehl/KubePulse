# Container Health Checks vs System Safety

Kubernetes health checks are necessary but not sufficient for release safety.

## Health Checks

Kubernetes readiness and liveness probes usually answer:

- is the container running?
- does the health endpoint respond?
- should this pod receive traffic?

They may not answer:

- are dependencies reachable?
- is p95/p99 latency within rollout budget?
- is the service in fallback-only mode?
- is a degraded path causing user-visible impact?
- is recovery stable?

## False-Green Condition

A false-green condition occurs when:

```json
{
  "probes_say_healthy": true,
  "safe_to_operate": false
}

The container remains healthy, but system behavior is unsafe.

Examples
Dependency Latency
service health endpoint responds
downstream database latency spikes
p95 and p99 latency drift upward
release should be blocked
DNS Failure
pod process remains healthy
dependency name resolution fails
user-facing path becomes unavailable
release should be blocked
Degraded Path
traffic still routes
alternate path adds unsafe latency
probes remain green
rollout should hold or block
KubePulse Safety Signals

KubePulse evaluates:

p50 / p95 / p99 latency
error rate
recovery window
dependency reachability
probe mismatch
degraded-path requests
rollout decision
Canonical Output
{
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "latency spike + probe false positive"
}
Why It Matters

Container health verifies process availability. KubePulse validates system safety.
