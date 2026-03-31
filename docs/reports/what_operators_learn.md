# What Operators Learn From KubePulse

KubePulse is designed to answer operationally useful questions:

- Did the system really recover, or did it only look healthy?
- Did p50 / p95 latency return to baseline?
- Did DNS, dependency reachability, or service-to-service communication remain degraded?
- Were readiness probes truthful, or did they produce false-positive health signals?
- Is the system safe to continue operating, or is there still rollout / failover risk?

## Most Important Signals

- recovery time
- p50 / p95 latency drift
- DNS failure result
- readiness mismatch / probe false positive
- rollout risk interpretation
- remediation confidence
