def detect_readiness_false_positive(
    readiness_before: str,
    readiness_after: str,
    error_rate: float,
    latency_p95_ms: float,
    latency_threshold_ms: float = 500,
    error_rate_threshold: float = 0.05
):
    """
    Detect readiness false positive where service is degraded but probe is still ready.
    """

    degraded = (
        latency_p95_ms > latency_threshold_ms or
        error_rate > error_rate_threshold
    )

    if readiness_before == "ready" and readiness_after == "ready" and degraded:
        return True

    return False
