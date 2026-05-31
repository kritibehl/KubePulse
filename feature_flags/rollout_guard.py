import json
from pathlib import Path

decision = json.loads(Path("feature_flags/kill_switch_decision.json").read_text())

print("KubePulse Feature Flag Rollout Guard")
print("===================================")
print(f"candidate_release_enabled: {decision['candidate_release_enabled']}")
print(f"rollback_kill_switch: {decision['rollback_kill_switch']}")
print(f"release_decision: {decision['release_decision']}")
print(f"reason: {decision['reason']}")
