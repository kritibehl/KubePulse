from __future__ import annotations

def _bounded_score(value: float) -> int:
    return max(0, min(100, int(round(value))))

def compute_network_health_score(report: dict) -> dict:
    dns_success_rate = float(report.get("dns_success_rate", 1.0))
    tcp_connect_latency_ms = float(report.get("tcp_connect_latency_ms", 0.0))
    http_success_rate = float(report.get("http_success_rate", 1.0))
    cross_zone_degradation_pct = float(report.get("cross_zone_degradation_pct", 0.0))
    path_recovery_time_seconds = float(report.get("path_recovery_time_seconds", report.get("recovery_window_seconds", 0.0)))
    readiness_false_positive = bool(report.get("readiness_false_positive", False))
    network_availability_gap_pct = float(report.get("network_availability_gap_pct", 0.0))

    dns_score = _bounded_score(dns_success_rate * 100)
    tcp_score = _bounded_score(100 - (tcp_connect_latency_ms / 3.0))
    http_score = _bounded_score(http_success_rate * 100)
    cross_zone_score = _bounded_score(100 - (cross_zone_degradation_pct * 2.5))
    recovery_score = _bounded_score(100 - (path_recovery_time_seconds * 4.5))
    readiness_integrity_score = 70 if readiness_false_positive else 100
    availability_alignment_score = _bounded_score(100 - (network_availability_gap_pct * 4))

    overall = round(
        (
            dns_score
            + tcp_score
            + http_score
            + cross_zone_score
            + recovery_score
            + readiness_integrity_score
            + availability_alignment_score
        ) / 7
    )

    return {
        "network_health_score": overall,
        "dns_score": dns_score,
        "tcp_score": tcp_score,
        "http_score": http_score,
        "cross_zone_score": cross_zone_score,
        "path_recovery_score": recovery_score,
        "readiness_integrity_score": readiness_integrity_score,
        "availability_alignment_score": availability_alignment_score,
    }
