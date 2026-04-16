from __future__ import annotations

from typing import Any, Dict, List


def build_remediation_plan(result: Dict[str, Any], rollout_risk: Dict[str, Any]) -> Dict[str, Any]:
    actions: List[str] = []
    reasoning: List[str] = []

    safe_to_operate = bool(result.get("safe_to_operate", True))
    readiness_false_positive = bool(result.get("readiness_false_positive", False))
    partial_recovery = bool(result.get("partial_recovery", False))
    latency_p95_drift_pct = float(result.get("latency_p95_drift_pct", 0.0) or 0.0)
    error_rate_delta = float(result.get("error_rate_delta", 0.0) or 0.0)
    path_extra_latency_ms = float(result.get("path_extra_latency_ms", 0.0) or 0.0)

    primary_action = "observe"

    if not safe_to_operate:
        primary_action = "reroute"
        actions.append("reroute_traffic")
        reasoning.append("System is not safe to operate")

    if rollout_risk.get("decision") == "hold_or_rollback":
        actions.append("pause_rollout")
        reasoning.append("Rollout risk is high")

    if readiness_false_positive:
        actions.append("tighten_readiness_probe")
        reasoning.append("Readiness stayed green despite degraded service quality")

    if latency_p95_drift_pct >= 100 or path_extra_latency_ms >= 75:
        actions.append("scale_target_service")
        reasoning.append("Latency inflation indicates degraded serving path or insufficient capacity")

    if error_rate_delta >= 0.02:
        actions.append("inspect_dependency_errors")
        reasoning.append("Error rate increased materially")

    if partial_recovery:
        actions.append("verify_failover_path")
        reasoning.append("Recovery completed on a degraded path")

    # preserve order, remove duplicates
    deduped_actions = []
    seen = set()
    for action in actions:
        if action not in seen:
            deduped_actions.append(action)
            seen.add(action)

    if rollout_risk.get("decision") == "hold_or_rollback" and not safe_to_operate:
        deployment_decision = "rollback_candidate"
        urgency = "high"
    elif rollout_risk.get("decision") == "deploy_with_caution":
        deployment_decision = "deploy_with_caution"
        urgency = "medium"
    else:
        deployment_decision = "deploy"
        urgency = "low"

    if deduped_actions:
        primary_action = deduped_actions[0]

    return {
        "primary_action": primary_action,
        "secondary_actions": deduped_actions[1:],
        "all_actions": deduped_actions,
        "reasoning": reasoning,
        "urgency": urgency,
        "deployment_decision": deployment_decision,
        "operator_goal": "restore safe-to-operate state" if not safe_to_operate else "maintain healthy rollout posture",
    }
