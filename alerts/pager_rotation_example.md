# Pager Rotation Example

## Primary On-call

- Platform Engineer
- Response target: 5 minutes
- Scope: release blocks, unsafe rollout decisions, SLO budget violations

## Secondary On-call

- SRE / Reliability Engineer
- Response target: 15 minutes
- Scope: unresolved incidents, rollback review, degraded dependency investigation

## Escalation Flow

detected -> acknowledged -> assigned -> rollback_review -> remediated -> closed
