from datetime import datetime, timedelta, timezone
import uuid

from app.dependency_graph_simulator import simulate_dependency_impact
from app.kpi_budget_engine import evaluate_kpi_budgets
from app.release_decision_engine import classify_release_decision


def run_multi_service_failure() -> dict:
    started = datetime.now(timezone.utc)
    ended = started + timedelta(seconds=12)

    report = {
        "run_id": uuid.uuid4().hex,
        "scenario": "multi_service_cascade",
        "pod_name": "edge-api",
        "namespace": "default",
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "success": False,
        "status": "fail",

        "readiness_before": "ready",
        "readiness_after": "ready",
        "readiness_false_positive": True,
        "probe_mismatch": True,
        "probes_say_healthy": True,
        "safe_to_operate": False,

        "latency_p50_ms": 240.0,
        "latency_p95_ms": 780.0,
        "latency_p99_ms": 1200.0,
        "error_rate": 0.08,
        "restart_count": 0,
        "recovery_window_seconds": 12.0,
        "availability_achieved_pct_simulated": 91.0,

        "baseline_latency_p50_ms": 90.0,
        "baseline_latency_p95_ms": 180.0,
        "baseline_latency_p99_ms": 320.0,
        "baseline_error_rate": 0.0,
        "observed_latency_p50_ms": 240.0,
        "observed_latency_p95_ms": 780.0,
        "observed_latency_p99_ms": 1200.0,
        "observed_error_rate": 0.08,

        "latency_p50_drift_pct": 166.67,
        "latency_p95_drift_pct": 333.33,
        "latency_p99_drift_pct": 275.0,
        "error_rate_delta": 0.08,

        "cross_zone_degradation_pct": 22.0,
        "path_changes_total": 2,
        "degraded_path_requests_total": 37,
        "path_extra_latency_ms": 410.0,
        "path_recovery_time_seconds": 12.0,
        "network_availability_gap_pct": 9.0,

        "failure_propagation": [
            "postgres latency spike",
            "auth retry amplification",
            "api queue growth",
            "edge response degradation",
        ],
        "what_probes_missed": [
            "Downstream DB latency propagated upstream while probes stayed green.",
            "Tail latency exceeded SLO before container health changed.",
            "User-facing degradation occurred without a restart or readiness flip.",
        ],

        "pass_fail_reason": "Dependency latency propagated across services while readiness probes remained healthy.",
        "release_decision": "block",
        "reason": "latency spike + probe false positive",
        "recommendation": "block | Dependency latency propagation detected. Investigate downstream service before rollout.",
        "stdout": "Simulated multi-service cascade: edge -> api -> auth -> postgres",
        "stderr": "",
        "error": None,
    }

    report.update(simulate_dependency_impact("postgres", "latency_spike"))
    report.update(evaluate_kpi_budgets(report))
    report.update(classify_release_decision(report))

    # keep the explicit unsafe flag regardless of classifier defaults
    report["safe_to_operate"] = False
    report["release_decision"] = "block"
    report["reason"] = "latency spike + probe false positive"

    report["recommendation_action"] = "block" if report.get("safe_to_operate") is False else "continue"
    return report
