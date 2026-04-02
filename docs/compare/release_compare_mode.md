# Release Compare Mode

KubePulse can be used to compare service states and releases, not just run isolated disruptions.

## Comparison modes

### Baseline vs Disrupted
Used to validate how a healthy service changes under failure.

### Previous Version vs New Version
Used to validate whether a release regressed recovery, latency, availability, fallback quality, or SLO compliance.

### Service A vs Service B
Used to compare candidate implementations, fallbacks, or deployment variants.

## Signals to compare

- recovery time
- p95/p99 latency drift
- availability
- SLO pass/fail
- error-budget burn
- fallback success
- degraded-serving vs outage
- probe false positives

## Why this matters

This makes KubePulse useful for:
- release validation
- rollout safety checks
- platform reliability review
- backend and AI service regression detection
