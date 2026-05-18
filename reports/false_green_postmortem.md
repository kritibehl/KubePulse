# False-Green Deployment Postmortem

## Incident

Readiness probes remained healthy while p95 latency, error rate, and degraded-path requests violated release budgets.

## Root Cause

The deployment passed infrastructure-level readiness checks but failed operational SLO validation during burst-load serving conditions.

## Impact

- release blocked
- rollback review triggered
- sev1 alert generated
- dependency impact detected

## Detection

KubePulse detected the unsafe rollout using:
- SLO burn-rate analysis
- p95 regression checks
- rollback recommendation engine
- alert escalation workflows

## Lessons Learned

Health checks alone are insufficient for release validation because operational degradation may occur before readiness probes fail.

## Remediation

- rollback candidate release
- re-run canary comparison
- review dependency bottlenecks
- verify recovery metrics
