from __future__ import annotations
from typing import Dict, Any

DEFAULT_BUDGETS = {
    "latency_p95_ms": 400.0,
    "latency_p99_ms": 900.0,
    "recovery_window_seconds": 10.0,
    "error_rate": 0.03,
}

def evaluate_kpi_budgets(report: Dict[str, Any], budgets: Dict[str, float] | None = None) -> Dict[str, Any]:
    b = budgets or DEFAULT_BUDGETS

    checks = {
        "latency_budget_ok": float(report.get("latency_p95_ms", 0.0)) <= b["latency_p95_ms"],
        "tail_latency_budget_ok": float(report.get("latency_p99_ms", 0.0)) <= b["latency_p99_ms"],
        "recovery_budget_ok": float(report.get("recovery_window_seconds", 0.0)) <= b["recovery_window_seconds"],
        "error_budget_ok": float(report.get("error_rate", 0.0)) <= b["error_rate"],
    }

    violations = [k for k, ok in checks.items() if not ok]

    return {
        **checks,
        "budget_violations": violations,
        "budget_violation_count": len(violations),
        "kpi_budgets": b,
    }
