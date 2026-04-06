from __future__ import annotations

def build_resilience_explanation(report: dict) -> dict:
    breakdown = {
        "recovery_quality": report.get("recovery_score", 0),
        "latency_stability": report.get("latency_score", 0),
        "dependency_resilience": report.get("network_health_score", 0),
        "probe_trustworthiness": report.get("probe_integrity_score", 0),
        "operator_clarity": 95 if report.get("decision_artifact") else 40,
    }
    dominant_failure_factor = min(breakdown, key=breakdown.get)
    first_fix = (
        "tighten readiness probes and reroute traffic"
        if report.get("readiness_false_positive")
        else "stabilize degraded dependency path"
    )
    return {
        "resilience_score_breakdown": breakdown,
        "dominant_failure_factor": dominant_failure_factor,
        "first_fix_recommendation": first_fix,
    }
