import time
import math
import requests

def percentile(values, pct):
    if not values:
        return 0.0
    values = sorted(values)
    k = math.ceil((pct / 100) * len(values)) - 1
    k = max(0, min(k, len(values) - 1))
    return float(values[k])

def probe_endpoint(url: str, requests_count: int = 25, timeout: float = 2.0):
    latencies_ms = []
    errors = 0

    for _ in range(requests_count):
        start = time.perf_counter()
        try:
            response = requests.get(url, timeout=timeout)
            elapsed = (time.perf_counter() - start) * 1000
            latencies_ms.append(elapsed)

            if response.status_code >= 500:
                errors += 1
        except requests.RequestException:
            elapsed = (time.perf_counter() - start) * 1000
            latencies_ms.append(elapsed)
            errors += 1

    total = len(latencies_ms)
    error_rate = errors / total if total else 0.0

    return {
        "latency_p50_ms": round(percentile(latencies_ms, 50), 2),
        "latency_p95_ms": round(percentile(latencies_ms, 95), 2),
        "latency_p99_ms": round(percentile(latencies_ms, 99), 2),
        "error_rate": round(error_rate, 4),
    }
