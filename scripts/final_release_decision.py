import json
from pathlib import Path

decision = json.loads(Path("netroute_lab/release_decisions/network_aware_release_decision.json").read_text())

print("KubePulse Final Release Decision")
print("================================")
print(f"scenario: {decision['scenario']}")
print(f"safe_to_operate: {decision['safe_to_operate']}")
print(f"release_decision: {decision['release_decision']}")
print(f"dependency_risk_score: {decision['dependency_risk_score']}")
print(f"degraded_path: {decision['degraded_path']}")
print("blocked_reason:")
for reason in decision["blocked_reason"]:
    print(f"  - {reason}")
print("recommended_remediation:")
for action in decision["recommended_remediation"]:
    print(f"  - {action}")
