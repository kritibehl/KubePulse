# Bug Reproduction Template

## Title

Release gate failed to block unsafe rollout

## Environment

- KubePulse branch:
- Python version:
- Deployment event:
- Test command:

## Steps To Reproduce

1. Run release validation command.
2. Inspect release decision output.
3. Compare observed result to expected decision.

## Expected Result

`release_decision=block`

## Actual Result

Fill in observed behavior.

## Logs / Artifacts

- release decision JSON
- CloudWatch-style metric payload
- deployment wave summary
- screenshot/report

## Follow-Up

- classify severity
- add regression test
- update matrix
- re-run CI validation
