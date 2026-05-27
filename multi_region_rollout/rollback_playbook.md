# Multi-Region Rollback Playbook

## Trigger Conditions

Rollback review starts when:

- `release_decision=block`
- CloudWatch-style alarm is `ALARM`
- canary validation fails
- dependency risk score exceeds threshold
- site health is degraded
- error budget is breached

## Rollback Steps

1. Freeze the next deployment wave.
2. Notify platform on-call.
3. Preserve release evidence.
4. Roll back candidate release.
5. Re-run canary validation.
6. Re-check dependency health.
7. Continue rollout only after recovery state is healthy.

## Operational Outcome

KubePulse prevents unsafe releases from expanding past early rollout waves.
