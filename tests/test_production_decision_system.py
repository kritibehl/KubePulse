from validators.rollout_risk import compute_rollout_risk
from app.remediation_planner import build_remediation_plan
from reports.operator_action_plan import build_operator_action_plan


def test_high_risk_rollout_gets_hold_or_rollback():
    result = {
        "safe_to_operate": False,
        "readiness_false_positive": True,
        "partial_recovery": True,
        "latency_p95_drift_pct": 125.0,
        "error_rate_delta": 0.02,
        "recovery_window_seconds": 2.4,
        "cross_zone_degradation_pct": 18.0,
        "path_extra_latency_ms": 80.0,
        "path_changes_total": 1,
    }

    rollout_risk = compute_rollout_risk(result)
    remediation_plan = build_remediation_plan(result, rollout_risk)
    operator_action_plan = build_operator_action_plan(result, rollout_risk, remediation_plan)

    assert rollout_risk["level"] in {"medium", "high"}
    assert rollout_risk["decision"] in {"deploy_with_caution", "hold_or_rollback"}
    assert remediation_plan["primary_action"] in {"reroute_traffic", "pause_rollout", "observe"}
    assert operator_action_plan["verdict"] == "not_safe_to_operate"
    assert "recommended_actions" in operator_action_plan
