import json
from pathlib import Path

wave_config = json.loads(Path("deployment_waves/wave_config.json").read_text())
site = json.loads(Path("reports/site_health/edge_site_health_report.json").read_text())

print("KubePulse Deployment Wave Validation")
print("===================================")
print(f"deployment_id: {wave_config['deployment_id']}")
print(f"site: {site['site']}")
print(f"site_health: {site['site_health']}")
print(f"canary_validation: {site['canary_validation']}")
print(f"cloudwatch_alarm_state: {site['checks']['cloudwatch_alarm_state']}")
print(f"rollback_gate: {site['rollback_gate']}")
print(f"release_decision: {site['release_decision']}")
print(f"recommended_action: {site['recommended_action']}")

block = (
    site["site_health"] != "healthy"
    or site["canary_validation"] != "pass"
    or site["checks"]["cloudwatch_alarm_state"] == "ALARM"
    or site["rollback_gate"] == "triggered"
)

summary = {
    "deployment_id": wave_config["deployment_id"],
    "wave_status": "blocked" if block else "continue",
    "freeze_next_wave": block,
    "rollback_required": block,
    "reason": "site health, canary, or CloudWatch alarm check failed" if block else "all checks passed"
}

out = Path("deployment_waves/wave_validation_summary.json")
out.write_text(json.dumps(summary, indent=2))

print("\nsummary:")
print(json.dumps(summary, indent=2))
