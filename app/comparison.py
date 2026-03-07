def compare_baseline_to_run(baseline: dict, result: dict) -> dict:
    baseline_latency = baseline.get("latency_p95_ms", 0.0)
    observed_latency = result.get("latency_p95_ms", baseline_latency)

    baseline_error_rate = baseline.get("error_rate", 0.0)
    observed_error_rate = result.get("error_rate", baseline_error_rate)

    latency_drift_pct = 0.0
    if baseline_latency > 0:
        latency_drift_pct = ((observed_latency - baseline_latency) / baseline_latency) * 100.0

    error_rate_delta = observed_error_rate - baseline_error_rate

    return {
        "baseline_latency_p95_ms": baseline_latency,
        "observed_latency_p95_ms": observed_latency,
        "latency_drift_pct": latency_drift_pct,
        "baseline_error_rate": baseline_error_rate,
        "observed_error_rate": observed_error_rate,
        "error_rate_delta": error_rate_delta,
    }
