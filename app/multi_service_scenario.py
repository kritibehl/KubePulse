from datetime import datetime, timedelta, timezone
import uuid


def run_multi_service_failure() -> dict:
    started = datetime.now(timezone.utc)
    ended = started + timedelta(seconds=12)

    return {
        "run_id": uuid.uuid4().hex,
        "scenario": "multi_service_cascade",
        "pod_name": "edge-api",
        "namespace": "default",
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "success": False,
        "status": "fail",

        "dependency_chain": ["edge", "api", "auth", "postgres"],
        "dependency_edges": [
            {"source": "edge", "target": "api", "protocol": "http"},
            {"source": "api", "target": "auth", "protocol": "http"},
            {"source": "auth", "target": "postgres", "protocol": "tcp"},
        ],

        "readiness_before": "ready",
        "readiness_after": "ready",
        "readiness_false_positive": True,
        "probe_mismatch": True,

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

        "latency_p50_drift_pct": round(((240.0 - 90.0) / 90.0) * 100.0, 2),
        "latency_p95_drift_pct": round(((780.0 - 180.0) / 180.0) * 100.0, 2),
        "latency_p99_drift_pct": round(((1200.0 - 320.0) / 320.0) * 100.0, 2),
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
        "recommendation_action": "block",
        "recommendation": "Block rollout and investigate downstream database latency propagation.",
        "stdout": "Simulated multi-service cascade: edge -> api -> auth -> postgres",
        "stderr": "",
        "error": None,
    }
