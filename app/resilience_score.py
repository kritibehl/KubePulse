def compute_resilience_score(scorecard: dict) -> dict:
    """
    Compute a resilience score from scenario metrics.
    """

    recovery_time = scorecard.get("recovery_window_seconds", 0)
    latency_p95 = scorecard.get("latency_p95_ms", 0)
    error_rate = scorecard.get("error_rate", 0)
    probe_mismatch = scorecard.get("probe_mismatch", False)

    # Recovery score
    if recovery_time <= 5:
        recovery_score = 100
    elif recovery_time <= 10:
        recovery_score = 90
    elif recovery_time <= 20:
        recovery_score = 75
    else:
        recovery_score = 50

    # Latency stability score
    if latency_p95 <= 200:
        latency_score = 100
    elif latency_p95 <= 400:
        latency_score = 80
    else:
        latency_score = 60

    # Error score
    if error_rate == 0:
        error_score = 100
    elif error_rate <= 0.01:
        error_score = 90
    elif error_rate <= 0.05:
        error_score = 75
    else:
        error_score = 50

    # Probe integrity score
    probe_score = 0 if probe_mismatch else 100

    resilience_score = round(
        (recovery_score + latency_score + error_score + probe_score) / 4
    )

    return {
        "resilience_score": resilience_score,
        "recovery_score": recovery_score,
        "latency_score": latency_score,
        "error_score": error_score,
        "probe_integrity_score": probe_score,
    }
