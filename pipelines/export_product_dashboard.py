import json
from pathlib import Path

sla_path = Path("dataset_sla/dataset_sla_report.json")
rollout_path = Path("product_dashboard/rollout_dashboard.json")
out_path = Path("product_dashboard/product_summary.md")

sla = json.loads(sla_path.read_text())
rollout = json.loads(rollout_path.read_text())

lines = [
    "# KubePulse Product Summary",
    "",
    "## Dataset SLA",
    "",
    f"- Freshness: {sla['freshness_minutes']} min / SLA {sla['freshness_sla_minutes']} min ({sla['freshness_status']})",
    f"- Completeness: {sla['completeness_pct']}% / SLA {sla['completeness_sla_pct']}% ({sla['completeness_status']})",
    f"- Pipeline latency: {sla['pipeline_latency_seconds']}s / SLA {sla['pipeline_latency_sla_seconds']}s ({sla['latency_status']})",
    f"- Failed jobs: {sla['failed_jobs']} ({sla['failed_jobs_status']})",
    "",
    "## Rollout Dashboard",
    "",
    f"- Rollout count: {rollout['rollout_count']}",
    f"- Approved releases: {rollout['approved_releases']}",
    f"- Blocked releases: {rollout['blocked_releases']}",
    f"- Rollback required: {rollout['rollback_required']}",
    f"- Mean time to detect: {rollout['mean_time_to_detect_seconds']}s",
    f"- Latest release decision: {rollout['latest_release_decision']}",
]

out_path.write_text("\n".join(lines) + "\n")
print(f"Wrote {out_path}")
