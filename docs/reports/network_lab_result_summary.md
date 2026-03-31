# Network Lab Result Summary

## KubePulse Network Lab

Dependency path:

`edge -> api-service -> auth-service`

## Baseline vs Degraded Results

### DNS Failure
- baseline request success: **25/25**
- degraded request success: **0/25**

### API Path Latency Injection
- baseline request success: **25/25**
- degraded request success: **23/25**
- baseline p50 latency: **4.888 ms**
- degraded p50 latency: **1.462 s**
- baseline p95 latency: **10.120 ms**
- degraded p95 latency: **2.306 s**

## Why this matters

These experiments show that KubePulse measures whether a system is truly safe to operate after degradation, not just whether it still responds to simple health checks.
