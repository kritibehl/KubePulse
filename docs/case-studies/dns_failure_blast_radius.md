# Blast Radius Case Study: DNS Failure

## Scenario
A DNS failure was injected between `frontend` and `auth-service` under repeated baseline vs degraded runs.

## Dependency Path
`frontend -> auth-service -> shared-db`

## Observed Propagation
- DNS success rate dropped from 98.5% to 55.0%
- TCP connect latency increased from 18 ms to 145 ms
- HTTP success rate dropped from 99.0% to 72.0%
- p95 latency increased from 165 ms to 315 ms
- readiness false positives appeared during degraded runs

## Likely Root Cause
Cluster DNS resolution path

## Estimated Blast Radius
- frontend
- auth-service
- shared-db
- frontend-gateway

## Why It Matters
This experiment shows that KubePulse is not just a single-service health checker. It traces degradation along the service dependency path, estimates blast radius, and distinguishes network availability issues from misleading readiness signals.
