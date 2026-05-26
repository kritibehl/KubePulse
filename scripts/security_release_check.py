import json
from pathlib import Path

data = json.loads(
    Path("reports/security/deployment_security_report.json").read_text()
)

print("KubePulse Security Release Validation")
print("====================================")
print(f"severity: {data['severity']}")
print(f"safe_to_operate: {data['safe_to_operate']}")
print(f"release_decision: {data['release_decision']}")

print("\nviolations:")
for v in data["violations"]:
    print(f"  - {v}")

print("\nrecommended_action:")
for action in data["recommended_action"]:
    print(f"  - {action}")
