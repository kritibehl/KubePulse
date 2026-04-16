from __future__ import annotations
from typing import Dict, Any

def classify_release_decision(report: Dict[str, Any]) -> Dict[str, Any]:
    budget_violations = int(report.get("budget_violation_count", 0))
    false_positive = bool(report.get("readiness_false_positive", False))
    safe = bool(report.get("safe_to_operate", False))
    error_rate = float(report.get("error_rate", 0.0))
    latency_p95 = float(report.get("latency_p95_ms", 0.0))

    if not safe and (false_positive or budget_violations >= 2 or error_rate >= 0.05):
        level = "unsafe"
        action = "block"
    elif budget_violations == 1 or latency_p95 >= 350.0:
        level = "risky"
        action = "reroute"
    else:
        level = "safe"
        action = "continue"

    return {
        "release_safety_level": level,
        "release_decision": action,
    }
