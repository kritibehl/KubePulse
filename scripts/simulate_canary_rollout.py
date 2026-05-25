import json
from pathlib import Path

data = json.loads(Path("canary/rollout_simulation.json").read_text())

print("KubePulse Canary Rollout Simulation")
print("===================================")
print(f"release_id: {data['release_id']}")
print(f"strategy: {data['strategy']}")

final_decision = "continue"

for step in data["traffic_steps"]:
    print(
        f"{step['candidate_traffic_percent']}% traffic | "
        f"p95={step['p95_latency_ms']}ms | "
        f"error_rate={step['error_rate']} | "
        f"decision={step['decision']}"
    )
    if step["decision"] == "block":
        final_decision = "block"

print(f"final_release_decision: {final_decision}")
print(f"rollback_recommended: {data['rollback_recommended']}")
print(f"rollback_reason: {data['rollback_reason']}")
