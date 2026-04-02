# What Probes Missed

KubePulse is designed to catch cases where infrastructure health looked acceptable while user-facing quality was still degraded.

## Example 1 — DNS Failure
- readiness: green
- downstream dependency path: broken
- user-facing requests: failed
- KubePulse result: flagged real recovery gap and unsafe-to-operate state

## Example 2 — Vector DB Latency Degradation
- readiness: green
- retrieval path: available but slow
- user-facing latency: degraded beyond target
- fallback quality: partial
- KubePulse result: service still serving, but SLO violated and rollout risk remained

## Example 3 — Fallback Under Load
- probes: healthy
- requests: still served
- fallback success: degraded
- error budget: burned rapidly
- KubePulse result: degraded-serving mode detected, not safe to treat as healthy recovery

## Core idea

A service can look healthy and still be unsafe to operate.
KubePulse exists to detect that gap.
