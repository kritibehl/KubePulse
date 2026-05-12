# PagerDuty-Style Notification Example

## Alert

`KubePulseUnsafeRelease`

## Severity

`sev1`

## Timestamp

`2026-04-21T16:04:02Z`

## Affected Service

`checkout`

## Impacted Services

- `inventory`
- `payments`

## Release Decision

`block`

## Rollback Recommendation

Rollback recommended: `true`

Rollback candidate: `candidate_release`

## Escalation Target

`platform_oncall`

## Reason

- p95 latency regression
- error-rate budget violation
- dependency impact detected

## Runbook

`runbooks/release_block_response.md`

## Alert Pipeline

alert fired -> platform_oncall notified -> rollback review started -> remediation tracked
