from prometheus_client import Gauge, Counter

safe_to_operate_gauge = Gauge(
    "kubepulse_safe_to_operate",
    "Whether the current scenario is safe to operate: 1 safe, 0 unsafe",
)

probe_healthy_gauge = Gauge(
    "kubepulse_probe_healthy",
    "Whether readiness probes report healthy: 1 healthy, 0 unhealthy",
)

latency_p95_gauge = Gauge(
    "kubepulse_latency_p95_ms",
    "Observed p95 latency in milliseconds",
)

latency_p99_gauge = Gauge(
    "kubepulse_latency_p99_ms",
    "Observed p99 latency in milliseconds",
)

error_rate_gauge = Gauge(
    "kubepulse_error_rate",
    "Observed error rate",
)

recovery_time_gauge = Gauge(
    "kubepulse_recovery_time_seconds",
    "Observed recovery time in seconds",
)

release_block_counter = Counter(
    "kubepulse_release_block_total",
    "Total number of release-block decisions emitted",
)


def update_release_metrics(result: dict) -> None:
    safe = bool(result.get("safe_to_operate", False))
    probes_healthy = bool(result.get("probes_say_healthy", result.get("readiness_after") == "ready"))

    safe_to_operate_gauge.set(1 if safe else 0)
    probe_healthy_gauge.set(1 if probes_healthy else 0)

    latency_p95_gauge.set(float(result.get("latency_p95_ms", result.get("observed_latency_p95_ms", 0.0)) or 0.0))
    latency_p99_gauge.set(float(result.get("latency_p99_ms", result.get("observed_latency_p99_ms", 0.0)) or 0.0))
    error_rate_gauge.set(float(result.get("error_rate", result.get("observed_error_rate", 0.0)) or 0.0))
    recovery_time_gauge.set(float(result.get("recovery_window_seconds", result.get("recovery_time_seconds", 0.0)) or 0.0))

    if result.get("release_decision") == "block":
        release_block_counter.inc()
