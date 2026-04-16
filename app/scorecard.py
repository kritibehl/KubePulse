def build_scorecard(result):
    return {
        "latency": {
            "p50": result.get("latency_p50_ms"),
            "p95": result.get("latency_p95_ms"),
            "p99": result.get("latency_p99_ms"),
            "p95_drift_pct": result.get("latency_p95_drift_pct"),
        },
        "errors": {
            "error_rate": result.get("error_rate"),
            "delta": result.get("error_rate_delta"),
        },
        "availability": {
            "aligned": result.get("availability_alignment_score"),
        },
        "dependency": {
            "health": result.get("network_health_score"),
            "propagation": result.get("probable_source_of_degradation"),
        },
        "verdict": result.get("release_decision"),
    }
