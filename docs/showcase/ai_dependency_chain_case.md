# AI Dependency Chain Case

## Scenario
Vector DB slows down -> inference latency spikes -> fallback partially succeeds -> availability preserved but SLO violated.

## What KubePulse surfaces
- availability preserved
- p95/p99 latency drift increased sharply
- fallback success dropped below target
- degraded-serving mode detected
- error budget burned despite continued serving
- service not fully down, but not safe to treat as healthy

## Why this matters

This is the type of modern AI-service reliability issue that simple health checks miss:
the endpoint still responds, but user-visible quality is degraded and service objectives are violated.
