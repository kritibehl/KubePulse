# Rollback Frequency Report

## Summary

KubePulse records rollback-review frequency during staged release validation.

| Release | Decision | Rollback Required | Reason |
|---|---|---|---|
| release-101 | continue | false | within budget |
| release-102 | block | true | p95 latency regression |
| deploy-204 | block | true | CloudWatch alarm + dependency risk |

## Trend

Rollback reviews increased when canary validation and dependency-risk signals were evaluated together.

## Operational Recommendation

Continue tracking rollback frequency with deployment ID, wave, site, alarm state, dependency health, and error-budget burn.
