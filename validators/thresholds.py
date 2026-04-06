from __future__ import annotations

def evaluate_thresholds(report: dict, scenario_spec: dict) -> dict:
    t = scenario_spec.get("safe_to_operate_thresholds", {})
    availability_min = float(t.get("availability_min_pct", 99.0))
    p95_max = float(t.get("p95_max_ms", 300.0))
    p99_max = float(t.get("p99_max_ms", 500.0))
    error_rate_max = float(t.get("error_rate_max_pct", 1.0))

    availability = float(report.get("availability_achieved_pct", report.get("availability_achieved_pct_simulated", 0.0)))
    p95 = float(report.get("latency_p95_ms", 0.0))
    p99 = float(report.get("latency_p99_ms", 0.0))
    error_rate_pct = float(report.get("error_rate_achieved_pct", report.get("error_rate", 0.0) * 100.0))

    return {
        "availability_ok": availability >= availability_min,
        "p95_ok": p95 <= p95_max,
        "p99_ok": p99 <= p99_max,
        "error_rate_ok": error_rate_pct <= error_rate_max,
        "threshold_summary": {
            "availability": {"observed": availability, "min": availability_min},
            "p95_ms": {"observed": p95, "max": p95_max},
            "p99_ms": {"observed": p99, "max": p99_max},
            "error_rate_pct": {"observed": error_rate_pct, "max": error_rate_max},
        },
    }
