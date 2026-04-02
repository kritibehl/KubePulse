# What Probes Missed

KubePulse highlights cases where infrastructure health checks looked green but user-facing quality remained degraded.

## Examples

- readiness probe reported healthy while downstream DNS resolution was broken
- health checks passed while p95/p99 latency remained far above baseline
- service continued serving responses, but fallback quality dropped below target
- backend dependency recovered partially, but user-visible error budget was still exhausted

## Why this matters

This is the difference between:
- “the pod is up”
- and
- “the service is actually safe to operate”
