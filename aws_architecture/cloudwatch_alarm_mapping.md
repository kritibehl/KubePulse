# CloudWatch-Style Alarm Mapping

| Signal | Alarm | Threshold | Action |
|---|---|---:|---|
| SafeToOperate | UnsafeReleaseAlarm | == 0 | block rollout |
| LatencyP95Ms | HighLatencyAlarm | > 250 ms | rollback review |
| ErrorRate | ErrorBudgetAlarm | > 0.02 | block rollout |
| ReleaseBlockTotal | ReleaseBlockedAlarm | > 0 | freeze next wave |
| DependencyRiskScore | DependencyRiskAlarm | > 80 | rollback review |

## Alarm Outcome

When any critical alarm is in `ALARM`, the Lambda-style evaluator returns:

`release_decision=block`
