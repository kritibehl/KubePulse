import json
from pathlib import Path

data = json.loads(Path("hardware_validation/hardware_health_signal.json").read_text())
c = data["checks"]

violations = []

if not c["device_visible"]:
    violations.append("device_not_visible")
if not c["driver_runtime_ready"]:
    violations.append("driver_runtime_not_ready")
if c["memory_pressure_percent"] > 80:
    violations.append("high_memory_pressure")
if c["gpu_utilization_percent"] > 90:
    violations.append("gpu_saturation")
if c["p95_latency_ms"] > 500:
    violations.append("p95_latency_regression")
if c["error_rate"] > 0.02:
    violations.append("error_rate_budget_violation")

decision = {
    "device": data["device"],
    "violations": violations,
    "hardware_risk": "high" if violations else "low",
    "release_decision": "block" if violations else "continue",
    "rollback_required": bool(violations)
}

Path("hardware_validation/reports/hardware_release_decision.json").write_text(
    json.dumps(decision, indent=2)
)

print(json.dumps(decision, indent=2))
