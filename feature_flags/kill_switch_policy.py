import json
from pathlib import Path

config = json.loads(Path("feature_flags/flag_config.json").read_text())

slo_breached = True
dependency_risk_high = True

kill_switch_enabled = (
    config["policy"]["disable_candidate_on_slo_breach"] and slo_breached
) or (
    config["policy"]["disable_candidate_on_dependency_risk"] and dependency_risk_high
)

decision = {
    "candidate_release_enabled": not kill_switch_enabled,
    "rollback_kill_switch": kill_switch_enabled,
    "release_decision": "block" if kill_switch_enabled else "continue",
    "reason": "SLO breach or dependency risk triggered kill switch"
}

Path("feature_flags/kill_switch_decision.json").write_text(json.dumps(decision, indent=2))

print(json.dumps(decision, indent=2))
