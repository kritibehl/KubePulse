# Deployment Security Governance Summary

## Deployment

`deploy-204`

## Violations

| Violation | Severity |
|---|---|
| missing TLS | high |
| missing authentication | critical |
| insecure environment variable | high |
| missing resource limits | medium |

## Release Decision

`block`

## Operational Interpretation

KubePulse blocked deployment continuation because deployment policy validation detected insecure rollout conditions.

## Recommended Remediation

- enable TLS
- enforce authentication
- remove insecure environment variables
- configure Kubernetes resource limits
