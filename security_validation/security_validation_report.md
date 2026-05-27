# Security Validation Report

## Insecure Deployment

Expected decision: `block`

Detected issues:

- missing TLS
- missing authentication
- insecure environment variables
- missing resource limits
- missing liveness probe

## Secure Deployment

Expected decision: `continue`

Validated controls:

- TLS annotation present
- authentication annotation present
- no insecure env vars
- readiness/liveness probes present
- resource limits present

## Release Safety Impact

KubePulse blocks deployment continuation when deployment policy checks detect unsafe rollout conditions.
