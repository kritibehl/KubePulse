# Architecture Diagram

KubePulse evaluates service-path resilience across a simple dependency chain:

`edge -> api -> auth -> downstream`

This is intentionally easy to understand.

## What the diagram shows
- request path through the service chain
- where a failure or degraded hop occurs
- how KubePulse converts path behavior into an operator decision:
  - probes healthy?
  - SLO met?
  - safe to operate?
  - what probes missed?
  - recommendation

## Why it matters
The architecture diagram makes KubePulse legible to both technical and non-technical reviewers by connecting topology, degradation, and final operational decision in one place.
