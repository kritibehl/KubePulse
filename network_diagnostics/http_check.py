import time
import urllib.request
from network_diagnostics.checks import result


def run_http_check(url: str, timeout_seconds: float = 1.0) -> dict:
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            status = response.getcode()
            if 200 <= status < 400:
                return result("http_health", "pass", url, f"HTTP health returned {status}", elapsed)
            return result("http_health", "fail", url, f"HTTP health returned {status}", elapsed)
    except Exception as e:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return result("http_health", "fail", url, f"HTTP health failed: {e}", elapsed)
