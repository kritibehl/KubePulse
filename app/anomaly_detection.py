def classify_anomalies(report: dict) -> list[str]:
    anomalies = []

    if report.get("readiness_false_positive", False):
        anomalies.append("readiness_false_positive")

    if report.get("latency_p95_ms", 0.0) > 500:
        anomalies.append("high_latency")

    if report.get("error_rate", 0.0) > 0.05:
        anomalies.append("error_spike")

    if report.get("restart_count", 0) > 2:
        anomalies.append("restart_instability")

    return anomalies
