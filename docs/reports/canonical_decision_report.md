# Canonical Decision Report

## Scenario
**link_failure_failover**

## Decision
- **probes healthy?** yes
- **SLO met?** no
- **safe to operate?** no
- **recommendation:** reroute

## Key metrics
- convergence: **2.4s**
- path changes: **1**
- degraded-path requests: **12**
- p95 drift: **125%**
- p99 drift: **109.52%**
- extra path latency: **80 ms**
- estimated path latency after reroute: **80 ms -> 150 ms**

## What probes missed
- readiness stayed green while requests shifted onto a degraded failover path
- user-facing latency increased even after reachability recovered
- path recovered partially, but safe-to-operate checks still failed

## Paths
- baseline: `edge -> router-a -> api -> auth -> downstream`
- final: `edge -> router-a -> auth -> downstream`

## Operator interpretation
KubePulse marked this scenario as **unsafe to operate** even though probes remained healthy, because failover restored reachability but not acceptable service quality.
