# Baseline vs Degraded vs Recovered

| State | Convergence | Availability | p95/p99 Drift | Error-Budget Burn | Safe to Operate? | Interpretation |
|---|---:|---:|---:|---:|---|---|
| Baseline | 0.0s | 100% | minimal | none | yes | healthy path |
| Degraded | scenario-dependent | reduced or unstable | elevated | significant to full | no | service may still respond, but quality is degraded |
| Recovered | restored after reroute/failover | improved | may remain elevated | may still be consumed | depends | recovery may be partial, not automatically safe |

## Example: Link Failure Failover
- baseline path latency: **80 ms**
- degraded / rerouted path latency: **150 ms**
- convergence: **2.4s**
- probes healthy: **yes**
- safe to operate: **no**

## Example: Blackhole
- availability: **0%**
- unreachable window: **18.0s**
- degraded-path requests: **25**
- recommendation: **block**

## Example: Link Flap
- path changes: **6**
- convergence: **6.0s**
- degraded-path requests: **18**
- recommendation: **reroute / stabilize path before continuing**

## Why this matters
KubePulse is useful not just for disruption testing, but for deciding whether a system has actually recovered enough to continue rollout or restore traffic.
