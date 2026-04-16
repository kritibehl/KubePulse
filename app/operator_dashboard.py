def build_operator_dashboard(report: dict) -> dict:
    return {
        "summary": {
            "scenario": report.get("scenario"),
            "safe_to_operate": report.get("safe_to_operate"),
            "release_decision": report.get("release_decision"),
        },
        "kpis": {
            "latency_p95_ms": report.get("latency_p95_ms"),
            "latency_p99_ms": report.get("latency_p99_ms"),
            "error_rate": report.get("error_rate"),
            "resilience_score": report.get("resilience_score"),
            "network_health_score": report.get("network_health_score"),
        },
        "probe_gap": {
            "probes_say_healthy": report.get("probes_say_healthy"),
            "readiness_false_positive": report.get("readiness_false_positive"),
            "what_probes_missed": report.get("what_probes_missed"),
        },
    }
