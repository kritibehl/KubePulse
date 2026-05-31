# Error-Budget Release Gate Report

## Summary

KubePulse evaluated release safety using SLO/error-budget signals.

## Result

```json
{
  "slo": "99.9",
  "error_budget_remaining": "4.2%",
  "fast_burn_detected": true,
  "release_decision": "block",
  "reason": "p95 latency and error rate consumed budget too quickly"
}
Signals
p95 latency exceeded budget
error rate exceeded budget
dependency risk exceeded threshold
release freeze required
