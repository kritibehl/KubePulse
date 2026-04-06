from __future__ import annotations

def build_probe_gap(report: dict) -> dict:
    readiness_false_positive = bool(report.get("readiness_false_positive", False))
    probes_healthy = bool(report.get("probes_say_healthy", False))
    safe = bool(report.get("safe_to_operate", False))

    summary = []
    if probes_healthy and not safe:
        summary.append("probes remained healthy while safe-to-operate stayed false")
    if readiness_false_positive:
        summary.append("readiness reported healthy despite degraded dependency-path behavior")
    if report.get("status") == "fail" and probes_healthy:
        summary.append("probe recovery or liveness signal overstated real service health")

    return {
        "probe_gap_summary": summary,
        "probe_gap_report": {
            "probes_healthy": probes_healthy,
            "readiness_false_positive": readiness_false_positive,
            "safe_to_operate": safe,
            "gap_detected": len(summary) > 0,
        },
    }
