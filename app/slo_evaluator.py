from __future__ import annotations

def evaluate_slo(report: dict) -> dict:
    slo = report.get("slo") or {}
    availability_target = float(slo.get("availability_target", 99.5))
    latency_p99_target_ms = float(slo.get("latency_p99_target_ms", 500.0))
    error_rate_target = float(slo.get("error_rate_target", 1.0))
    window_minutes = int(slo.get("window_minutes", 30))

    success = bool(report.get("success", False))
    error_rate_fraction = float(report.get("error_rate", 0.0))
    latency_p99_ms = float(report.get("latency_p99_ms", 0.0))

    availability_achieved = 100.0 if success else 0.0
    error_rate_achieved = round(error_rate_fraction * 100.0, 3)

    availability_met = availability_achieved >= availability_target
    latency_met = latency_p99_ms <= latency_p99_target_ms
    error_rate_met = error_rate_achieved <= error_rate_target
    slo_met = availability_met and latency_met and error_rate_met

    allowed_error_budget_pct = round(100.0 - availability_target, 3)
    actual_burn_pct = round(max(0.0, 100.0 - availability_achieved), 3)

    if allowed_error_budget_pct == 0:
        error_budget_remaining_pct = 0.0 if actual_burn_pct > 0 else 100.0
    else:
        error_budget_remaining_pct = round(
            max(0.0, 100.0 * (1.0 - (actual_burn_pct / allowed_error_budget_pct))),
            3,
        )

    return {
        "slo_availability_target": availability_target,
        "slo_latency_p99_target_ms": latency_p99_target_ms,
        "slo_error_rate_target": error_rate_target,
        "slo_window_minutes": window_minutes,
        "availability_achieved_pct": round(availability_achieved, 3),
        "latency_p99_achieved_ms": round(latency_p99_ms, 3),
        "error_rate_achieved_pct": error_rate_achieved,
        "error_budget_remaining_pct": error_budget_remaining_pct,
        "slo_met": slo_met,
        "slo_summary": {
            "availability": {"achieved_pct": round(availability_achieved, 3), "target_pct": availability_target, "met": availability_met},
            "latency_p99": {"achieved_ms": round(latency_p99_ms, 3), "target_ms": latency_p99_target_ms, "met": latency_met},
            "error_rate": {"achieved_pct": error_rate_achieved, "target_pct": error_rate_target, "met": error_rate_met},
        },
    }
