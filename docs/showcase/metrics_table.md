# Compact Metrics Table

| Metric | Validated Result |
|---|---|
| Failover convergence | **2.4s** |
| Blackhole unreachable window | **18.0s** |
| Link-flap path changes | **6** |
| Path latency after reroute | **80 ms -> 150 ms** |
| Link-failure degraded-path requests | **12** |
| Blackhole degraded-path requests | **25** |
| Link-flap degraded-path requests | **18** |
| Asymmetric-path degraded-path requests | **9** |

## Reading this table
These metrics make KubePulse legible as an operational decision tool:
- how fast failover converged
- whether the system became unreachable
- whether route churn caused instability
- whether reroute restored only reachability or real service quality
