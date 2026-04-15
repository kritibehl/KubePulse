from __future__ import annotations
from typing import Dict, Any

def apply_release_gate(report: Dict[str, Any]) -> Dict[str, Any]:
    safe = bool(report.get("safe_to_operate", False))
    p95 = float(report.get("latency_p95_ms", 0.0))
    err = float(report.get("error_rate", 0.0))
    false_green = bool(report.get("readiness_false_positive", False))

    if not safe or false_green:
        decision = "block"
        reason = "latency spike + probe false positive"
    elif p95 >= 350.0 or err >= 0.03:
        decision = "hold"
        reason = "budget pressure under degraded conditions"
    else:
        decision = "continue"
        reason = "within safety and latency budgets"

    return {
        "release_decision": decision,
        "reason": reason,
    }
