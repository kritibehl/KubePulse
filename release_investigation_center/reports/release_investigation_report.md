# Release Investigation Center Report

## Summary

KubePulse investigated a bad deployment and produced root-cause candidates, affected dependencies, rollback recommendation, degraded regions, blast radius, and customer-impact classification.

## Output

```json
{
  "likely_root_cause": "dns_resolution_instability",
  "affected_dependencies": ["api", "payments", "database"],
  "blast_radius": "high",
  "rollback_recommendation": true,
  "freeze_next_wave": true,
  "release_decision": "block",
  "customer_impact": "high"
}
Why This Matters

This turns KubePulse from release validation into an internal deployment safety platform that helps teams investigate bad rollouts and decide whether to rollback, freeze, or continue.
