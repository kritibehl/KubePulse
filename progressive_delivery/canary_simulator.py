import json
from pathlib import Path

steps = [
    {"step": "10% traffic", "p95_regression": "+12%", "analysis_result": "passed", "rollback_triggered": False},
    {"step": "25% traffic", "p95_regression": "+184%", "analysis_result": "failed", "rollback_triggered": True},
]

report = {
    "rollout": "kubepulse-progressive-rollout",
    "steps": steps,
    "final_decision": "rollback",
    "reason": "p95 regression exceeded canary analysis threshold"
}

Path("progressive_delivery/reports/canary_analysis_report.json").write_text(json.dumps(report, indent=2))

print(json.dumps(report, indent=2))
