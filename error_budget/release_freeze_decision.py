import json
from pathlib import Path
from burn_rate_calculator import calculate_burn_rate

result = calculate_burn_rate()

decision = {
    **result,
    "release_decision": "block" if result["fast_burn_detected"] else "continue",
    "freeze_release": result["fast_burn_detected"],
    "reason": "p95 latency and error rate consumed budget too quickly"
}

Path("error_budget/reports/error_budget_decision.json").write_text(json.dumps(decision, indent=2))

print(json.dumps(decision, indent=2))
