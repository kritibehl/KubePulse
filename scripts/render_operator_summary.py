import json
from pathlib import Path

incident_dir = Path("investigations/sample_incident")
report_dir = Path("reports")

report_dir.mkdir(exist_ok=True)

timeline = json.loads((incident_dir / "deployment_timeline.json").read_text())
correlation = json.loads((incident_dir / "deployment_correlation.json").read_text())
rollback = json.loads((incident_dir / "rollback_recommendation.json").read_text())

report = f"""
# KubePulse Release Investigation Report

## Release

Release ID: {timeline["release_id"]}

## Timeline

- Deployment start: {timeline["deployment_start"]}
- Latency regression detected: {timeline["latency_regression_detected"]}
- Error-rate increase detected: {timeline["error_rate_increase_detected"]}
- Release blocked: {timeline["release_blocked"]}
- Rollback review started: {timeline["rollback_review_started"]}

## Correlated Signals

- p95 latency regression: {correlation["signals"]["p95_latency_regression_percent"]}%
- Error-rate increase: {correlation["signals"]["error_rate_increase_percent"]}%
- Probe healthy: {correlation["signals"]["probe_healthy"]}
- Safe to operate: {correlation["signals"]["safe_to_operate"]}

## Suspected Root Cause

{correlation["suspected_root_cause"]}

## Rollback Recommendation

Rollback recommended: {rollback["rollback_recommended"]}

Reasons:
"""

for r in rollback["reason"]:
    report += f"- {r}\n"

report += f"""
Recommended action:
{rollback["recommended_action"]}
"""

out = report_dir / "release_investigation_report.md"
out.write_text(report)

print(f"wrote {out}")
