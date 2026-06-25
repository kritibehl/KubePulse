import socket
import time
from network_diagnostics.checks import result


def run_tcp_check(host: str, port: int, timeout_seconds: float = 1.0) -> dict:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            return result("tcp_reachability", "pass", f"{host}:{port}", "TCP connection succeeded", elapsed)
    except Exception as e:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        return result("tcp_reachability", "fail", f"{host}:{port}", f"TCP connection failed: {e}", elapsed)
