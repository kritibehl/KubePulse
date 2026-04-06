from __future__ import annotations

from typing import Any, Dict


def build_operator_action_plan(
    result: Dict[str, Any],
    rollout_risk: Dict[str, Any],
    remediation_plan: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "verdict": "not_safe_to_operate" if not bool(result.get("safe_to_operate", True)) else "safe_to_operate",
        "deployment_decision": remediation_plan.get("deployment_decision"),
        "rollout_risk": rollout_risk,
        "recommended_actions": remediation_plan.get("all_actions", []),
        "primary_action": remediation_plan.get("primary_action"),
        "why": rollout_risk.get("reasons", []),
        "key_metrics": {
            "latency_p95_drift_pct": result.get("latency_p95_drift_pct"),
            "error_rate_delta": result.get("error_rate_delta"),
            "recovery_window_seconds": result.get("recovery_window_seconds"),
            "path_extra_latency_ms": result.get("path_extra_latency_ms"),
            "readiness_false_positive": result.get("readiness_false_positive"),
            "safe_to_operate": result.get("safe_to_operate"),
        },
    }
