import json
from pathlib import Path

data = json.loads(Path("rollback/canary_failure_rollback_simulation.json").read_text())

print("KubePulse Canary Failure Rollback Simulation")
print("===========================================")
print(f"release_id: {data['release_id']}")
print(f"stage: {data['rollout']['stage']}")
print(f"failed_deployment: {data['rollout']['failed_deployment']}")
print(f"degraded_dependency: {data['signals']['dependency']}")
print(f"safe_to_operate: {data['signals']['safe_to_operate']}")
print(f"automatic_rollback_triggered: {data['rollback']['automatic_rollback_triggered']}")
print(f"rollback_target: {data['rollback']['rollback_target']}")
print(f"release_freeze: {data['rollback']['release_freeze']}")
print(f"release_decision: {data['release_decision']}")
