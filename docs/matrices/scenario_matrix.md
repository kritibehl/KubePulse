# Scenario Matrix

| Scenario | Recovery Time | p95/p99 Drift | Availability | Fallback Success | Error-Budget Burn | Degraded-Serving vs Outage |
|---|---:|---:|---:|---:|---:|---|
| Pod kill | measured | measured | measured | N/A or measured | measured | degraded or recovered |
| CPU stress | measured | measured | measured | N/A or measured | measured | degraded-serving |
| Network partition | measured | measured | measured | measured | measured | degraded or outage |
| DNS failure | measured | measured | measured | measured | measured | degraded or outage |
| Inference timeout spike | measured | measured | measured | measured | measured | degraded-serving |
| Vector DB latency degradation | measured | measured | measured | measured | measured | degraded-serving |
| Embedding-service outage | measured | measured | measured | measured | measured | outage |
| Fallback under load | measured | measured | measured | measured | measured | degraded-serving |

## What this matrix shows

KubePulse validates whether a backend or AI service is actually safe to operate after disruption by comparing recovery behavior, user-visible latency, availability, fallback quality, and budget consumption across failure types.
