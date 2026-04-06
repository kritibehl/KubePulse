# Green Metrics Can Be Misleading

## Scenario
**link_failure_failover**

## What the probes said
- readiness: healthy
- service: up
- basic health signal: green

## What KubePulse found
- path changed after failure
- requests shifted onto a degraded route
- user-facing latency increased
- SLO checks failed
- service was **not safe to operate**

## Decision
- **probes healthy?** yes
- **SLO met?** no
- **safe to operate?** no
- **recommendation:** reroute

## Why this matters
This is the exact gap KubePulse is designed to catch:
the system looked healthy, but recovery was only partial and operational safety had not actually been restored.
