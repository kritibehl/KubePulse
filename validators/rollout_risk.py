from __future__ import annotations

from typing import Any, Dict, List


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def compute_rollout_risk(result: Dict[str, Any]) -> Dict[str, Any]:
    score = 0.0
    reasons: List[str] = []

    safe_to_operate = bool(result.get("safe_to_operate", True))
    readiness_false_positive = bool(result.get("readiness_false_positive", False))
    partial_recovery = bool(result.get("partial_recovery", False))

    latency_p95_drift_pct = float(result.get("latency_p95_drift_pct", 0.0) or 0.0)
    error_rate_delta = float(result.get("error_rate_delta", 0.0) or 0.0)
    recovery_window_seconds = float(result.get("recovery_window_seconds", 0.0) or 0.0)
    cross_zone_degradation_pct = float(result.get("cross_zone_degradation_pct", 0.0) or 0.0)
    path_extra_latency_ms = float(result.get("path_extra_latency_ms", 0.0) or 0.0)
    path_changes_total = int(result.get("path_changes_total", 0) or 0)

    if not safe_to_operate:
        score += 30
        reasons.append("System marked not safe to operate")

    if readiness_false_positive:
        score += 20
        reasons.append("Readiness false positive detected")

    if latency_p95_drift_pct >= 100:
        score += 20
        reasons.append(f"High p95 latency drift: {latency_p95_drift_pct:.2f}%")
    elif latency_p95_drift_pct >= 50:
        score += 12
        reasons.append(f"Elevated p95 latency drift: {latency_p95_drift_pct:.2f}%")
    elif latency_p95_drift_pct > 20:
        score += 6
        reasons.append(f"Moderate p95 latency drift: {latency_p95_drift_pct:.2f}%")

    if error_rate_delta >= 0.05:
        score += 15
        reasons.append(f"Large error-rate increase: {error_rate_delta:.2%}")
    elif error_rate_delta >= 0.02:
        score += 8
        reasons.append(f"Elevated error-rate increase: {error_rate_delta:.2%}")
    elif error_rate_delta > 0:
        score += 4
        reasons.append(f"Observed error-rate increase: {error_rate_delta:.2%}")

    if recovery_window_seconds >= 10:
        score += 10
        reasons.append(f"Slow recovery window: {recovery_window_seconds:.2f}s")
    elif recovery_window_seconds >= 3:
        score += 6
        reasons.append(f"Moderate recovery window: {recovery_window_seconds:.2f}s")
    elif recovery_window_seconds > 0:
        score += 2
        reasons.append(f"Recovery window observed: {recovery_window_seconds:.2f}s")

    if partial_recovery:
        score += 8
        reasons.append("Only partial recovery achieved")

    if cross_zone_degradation_pct >= 20:
        score += 6
        reasons.append(f"Cross-zone degradation observed: {cross_zone_degradation_pct:.2f}%")
    elif cross_zone_degradation_pct >= 10:
        score += 3
        reasons.append(f"Cross-zone degradation present: {cross_zone_degradation_pct:.2f}%")

    if path_extra_latency_ms >= 75:
        score += 6
        reasons.append(f"Degraded path added {path_extra_latency_ms:.2f} ms latency")
    elif path_extra_latency_ms >= 30:
        score += 3
        reasons.append(f"Path reroute added {path_extra_latency_ms:.2f} ms latency")

    if path_changes_total >= 2:
        score += 5
        reasons.append(f"Multiple path changes detected: {path_changes_total}")
    elif path_changes_total == 1:
        score += 2
        reasons.append("Path reroute detected")

    score = round(_clamp(score), 2)

    if score >= 75:
        level = "high"
        decision = "hold_or_rollback"
    elif score >= 45:
        level = "medium"
        decision = "deploy_with_caution"
    else:
        level = "low"
        decision = "deploy"

    return {
        "score": score,
        "level": level,
        "decision": decision,
        "reasons": reasons,
    }
