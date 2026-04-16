def compare_baseline_candidate(baseline: dict, candidate: dict) -> dict:
    def pct(new, old):
        if old == 0:
            return 0.0
        return round(((new - old) / old) * 100.0, 2)

    return {
        "latency_p95_delta_pct": pct(candidate.get("latency_p95_ms", 0.0), baseline.get("latency_p95_ms", 0.0)),
        "latency_p99_delta_pct": pct(candidate.get("latency_p99_ms", 0.0), baseline.get("latency_p99_ms", 0.0)),
        "error_budget_delta": round(candidate.get("error_rate", 0.0) - baseline.get("error_rate", 0.0), 4),
        "regression_verdict": "regressed" if candidate.get("latency_p95_ms", 0.0) > baseline.get("latency_p95_ms", 0.0) else "stable",
    }
