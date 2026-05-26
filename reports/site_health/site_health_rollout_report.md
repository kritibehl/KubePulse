# Edge-Site Deployment Wave Health Report

## Deployment

Deployment ID: `deploy-204`

Strategy: wave-based rollout

## Site

`edge-site-atl1`

## Health Signals

| Signal | Status |
|---|---|
| DNS resolution | pass |
| TCP connectivity | pass |
| TLS health | pass |
| Container health | pass |
| p95 latency | 620 ms |
| p99 latency | 910 ms |
| Error rate | 5% |
| CloudWatch alarm | ALARM |

## Decision

`release_decision=block`

## Rollback Gate

`triggered`

## Recommended Action

Freeze next deployment wave and rollback candidate release.

## Operational Interpretation

The site remained reachable, but latency, error-rate, and alarm state indicated unsafe rollout behavior. KubePulse blocked the wave and recommended rollback before expanding traffic to additional sites.
