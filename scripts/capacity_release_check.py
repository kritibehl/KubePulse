import json
from pathlib import Path

data = json.loads(Path("reports/capacity/load_test_summary.json").read_text())

print("KubePulse Capacity Release Check")
print("================================")
print(f"tool: {data['tool']}")
print(f"peak_vus: {data['vus_peak']}")
print(f"p95_latency_ms: {data['p95_latency_ms']}")
print(f"p99_latency_ms: {data['p99_latency_ms']}")
print(f"error_rate: {data['error_rate']}")
print(f"autoscaling_recommended: {data['autoscaling_recommended']}")
print(f"release_ready: {data['release_ready']}")
print(f"release_decision: {data['release_decision']}")
print(f"reason: {data['reason']}")
