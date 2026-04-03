# What Probes Missed

This is the core KubePulse idea:

> A service can look healthy and still be unsafe to operate.

## Examples

### Link Failure Failover
- readiness: green
- dependency path: rerouted
- user-facing quality: degraded
- KubePulse result: **unsafe to operate**

### Blackhole
- some components may still look alive
- end-to-end path: unreachable
- user-facing availability: **0%**
- KubePulse result: **block**

### Link Flap
- probes: healthy
- path behavior: unstable
- route churn: repeated
- KubePulse result: **unsafe to operate despite no clean outage**

## Why it matters
KubePulse is built to catch the gap between:
- “service is up”
and
- “service is actually safe to operate”
