import json
from pathlib import Path

data = json.loads(Path("topology/service_dependency_health.json").read_text())

print("KubePulse Dependency Health Propagation")
print("======================================")
print(f"cascading_failure_detected: {data['cascading_failure_detected']}")
print(f"failure_root: {data['failure_root']}")
print(f"critical_path: {' -> '.join(data['critical_path'])}")
print(f"release_decision: {data['release_decision']}")
print("services:")
for svc, meta in data["services"].items():
    print(f"  - {svc}: {meta['health']} ({meta['role']})")
