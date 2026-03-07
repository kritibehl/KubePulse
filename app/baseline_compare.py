from app.metrics_probe import probe_endpoint


def collect_baseline(url: str) -> dict:
    return probe_endpoint(url, requests_count=25)


def compare_to_baseline(baseline: dict, observed: dict) -> dict:
    baseline_p50 = baseline.get("latency_p50_ms", 0.0)
    baseline_p95 = baseline.get("latency_p95_ms", 0.0)
    baseline_p99 = baseline.get("latency_p99_ms", 0.0)
    baseline_error_rate = baseline.get("error_rate", 0.0)

    observed_p50 = observed.get("latency_p50_ms", 0.0)
    observed_p95 = observed.get("latency_p95_ms", 0.0)
    observed_p99 = observed.get("latency_p99_ms", 0.0)
    observed_error_rate = observed.get("error_rate", 0.0)

    def pct_drift(baseline_value: float, observed_value: float) -> float:
        if baseline_value <= 0:
            return 0.0
        return round(((observed_value - baseline_value) / baseline_value) * 100.0, 2)

    return {
        "baseline_latency_p50_ms": baseline_p50,
        "baseline_latency_p95_ms": baseline_p95,
        "baseline_latency_p99_ms": baseline_p99,
        "baseline_error_rate": baseline_error_rate,
        "observed_latency_p50_ms": observed_p50,
        "observed_latency_p95_ms": observed_p95,
        "observed_latency_p99_ms": observed_p99,
        "observed_error_rate": observed_error_rate,
        "latency_p50_drift_pct": pct_drift(baseline_p50, observed_p50),
        "latency_p95_drift_pct": pct_drift(baseline_p95, observed_p95),
        "latency_p99_drift_pct": pct_drift(baseline_p99, observed_p99),
        "error_rate_delta": round(observed_error_rate - baseline_error_rate, 4),
    }
