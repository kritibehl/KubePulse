# Regional Wave Plan

## Goal

Limit blast radius during staged cloud rollout by validating one region or edge site before expanding traffic.

## Wave Strategy

| Wave | Region / Site | Traffic | Required Gates |
|---|---|---:|---|
| 1 | atl1 | 10% | canary, site health, CloudWatch alarm check |
| 2 | iad1 / ord1 | 25% | dependency health, p95/p99 latency, error budget |
| 3 | sfo1 / dfw1 | 50% | rollback gate clear, dependency risk score |
| 4 | global | 100% | all prior waves healthy |

## Release Decision Rule

Freeze next wave when:

- canary validation fails
- CloudWatch-style alarm enters `ALARM`
- dependency-risk score exceeds threshold
- site health is degraded
- rollback gate is triggered
