
def generate_recommendation(report):

    if report.get("readiness_false_positive"):
        return "Improve readiness probe to detect degraded state."

    if report["restart_count"] > 2:
        return "Investigate crash loops or memory pressure."

    if report["recovery_window_seconds"] > 20:
        return "Improve service startup or dependency recovery."

    return "System behavior within resilience thresholds."
