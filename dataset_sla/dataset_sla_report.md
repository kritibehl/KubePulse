# Dataset SLA Report

## Dataset

`validation_runs`

## Summary

| SLA Dimension | Observed | Target | Status |
|---|---:|---:|---|
| Freshness | 8 min | <= 30 min | pass |
| Completeness | 98.7% | >= 95.0% | pass |
| Pipeline latency | 42s | <= 120s | pass |
| Failed jobs | 0 | 0 | pass |

## Output

```json
{
  "freshness_minutes": 8,
  "completeness_pct": 98.7,
  "pipeline_latency_seconds": 42,
  "failed_jobs": 0,
  "sla_status": "pass"
}
Why This Matters

Release-safety dashboards depend on fresh and complete validation data. KubePulse tracks dataset freshness, completeness, pipeline latency, and failed jobs so rollout decisions are based on reliable data.
