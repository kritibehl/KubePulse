# Scenario Matrix

KubePulse validates whether backend and AI services are actually safe to operate after disruption.

| Scenario | Recovery Time | p95/p99 Drift | Availability | SLO Pass/Fail | Error-Budget Burn | Fallback Success | Degraded-Serving vs Outage | Probes False Positive? |
|---|---:|---:|---:|---|---:|---:|---|---|
| Pod kill | measured | measured | measured | evaluated | measured | N/A or measured | degraded or recovered | possible |
| DNS failure | measured | measured | measured | evaluated | measured | measured | degraded or outage | yes |
| CPU stress | measured | measured | measured | evaluated | measured | N/A or measured | degraded-serving | possible |
| Network partition | measured | measured | measured | evaluated | measured | measured | degraded or outage | yes |
| Inference timeout spike | measured | measured | measured | evaluated | measured | measured | degraded-serving | possible |
| Vector DB latency degradation | measured | measured | measured | evaluated | measured | measured | degraded-serving | possible |
| Embedding-service outage | measured | measured | measured | evaluated | measured | measured | outage | yes |
| Tool-router failure | measured | measured | measured | evaluated | measured | measured | degraded or outage | yes |
| Fallback under load | measured | measured | measured | evaluated | measured | measured | degraded-serving | possible |

## Why this matters

This matrix makes KubePulse legible at a glance:
- what failed
- how badly user-facing quality degraded
- whether probes were truthful
- whether the service was actually safe to operate
