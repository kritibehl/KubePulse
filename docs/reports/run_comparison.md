# Run Comparison

## Baseline vs Disrupted

Compare:
- recovery time
- p95/p99 drift
- availability
- fallback success
- error-budget burn
- degraded-serving vs outage

## Release A vs Release B

Compare:
- resilience score
- SLO pass/fail
- availability achieved
- p99 latency achieved
- fallback quality under dependency degradation
- user-visible degradation despite healthy probes

## Why this matters

KubePulse is not just a failure demo. It is a validation system for comparing whether one service state, release, or dependency path is safer to operate than another.
