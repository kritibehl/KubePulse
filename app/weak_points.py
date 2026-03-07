def suspected_weak_point(anomalies: list[str]) -> str:
    if "readiness_false_positive" in anomalies:
        return "health signaling"
    if "high_latency" in anomalies:
        return "degraded request path"
    if "error_spike" in anomalies:
        return "failure handling or dependency behavior"
    if "restart_instability" in anomalies:
        return "probe or restart stability"
    return "no major weak point detected"
