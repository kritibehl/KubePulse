def run_network_degradation(name: str) -> dict:
    profiles = {
        "packet_loss": {"packet_loss_pct": 12.0, "latency_p50_ms": 95.0, "latency_p95_ms": 420.0, "latency_p99_ms": 760.0, "error_rate": 0.06},
        "dns_failure": {"packet_loss_pct": 0.0, "latency_p50_ms": 110.0, "latency_p95_ms": 500.0, "latency_p99_ms": 880.0, "error_rate": 0.07},
        "partial_partition": {"packet_loss_pct": 8.0, "latency_p50_ms": 130.0, "latency_p95_ms": 620.0, "latency_p99_ms": 980.0, "error_rate": 0.09},
        "retry_storm": {"packet_loss_pct": 3.0, "latency_p50_ms": 150.0, "latency_p95_ms": 700.0, "latency_p99_ms": 1100.0, "error_rate": 0.10},
        "jitter": {"packet_loss_pct": 1.0, "latency_p50_ms": 110.0, "latency_p95_ms": 480.0, "latency_p99_ms": 820.0, "error_rate": 0.04},
        "intermittent_disconnect": {"packet_loss_pct": 3.0, "latency_p50_ms": 100.0, "latency_p95_ms": 450.0, "latency_p99_ms": 900.0, "error_rate": 0.07},
        "recovery_oscillation": {"packet_loss_pct": 5.0, "latency_p50_ms": 120.0, "latency_p95_ms": 560.0, "latency_p99_ms": 940.0, "error_rate": 0.08},
    }
    p = profiles[name]
    return {
        "scenario": name,
        "readiness_before": "ready",
        "readiness_after": "ready",
        "readiness_false_positive": True,
        "probe_mismatch": True,
        "probes_say_healthy": True,
        "safe_to_operate": False,
        "release_decision": "block",
        "reason": "latency spike + probe false positive",
        "packet_loss_pct": p["packet_loss_pct"],
        "latency_p50_ms": p["latency_p50_ms"],
        "latency_p95_ms": p["latency_p95_ms"],
        "latency_p99_ms": p["latency_p99_ms"],
        "error_rate": p["error_rate"],
        "stdout": f"Simulated network degradation: {name}",
        "stderr": "",
        "error": None,
    }
