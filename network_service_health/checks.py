import socket
import ssl
import time
import urllib.request


def dns_check(host: str) -> dict:
    try:
        ip = socket.gethostbyname(host)
        return {
            "check": "dns",
            "status": "pass",
            "target": host,
            "evidence": f"{host} resolved to {ip}",
        }
    except Exception as exc:
        return {
            "check": "dns",
            "status": "fail",
            "target": host,
            "evidence": f"DNS resolution failed: {exc}",
        }


def tcp_check(host: str, port: int, timeout_seconds: float = 2.0) -> dict:
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            return {
                "check": "tcp",
                "status": "pass",
                "target": f"{host}:{port}",
                "latency_ms": latency_ms,
                "evidence": "TCP connection succeeded",
            }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "check": "tcp",
            "status": "fail",
            "target": f"{host}:{port}",
            "latency_ms": latency_ms,
            "evidence": f"TCP connection failed: {exc}",
        }


def tls_check(host: str, port: int = 443, timeout_seconds: float = 2.0) -> dict:
    context = ssl.create_default_context()
    started = time.perf_counter()

    try:
        with socket.create_connection((host, port), timeout=timeout_seconds) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls_sock:
                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                certificate = tls_sock.getpeercert()
                return {
                    "check": "tls",
                    "status": "pass",
                    "target": f"{host}:{port}",
                    "latency_ms": latency_ms,
                    "protocol": tls_sock.version(),
                    "certificate_subject": certificate.get("subject", []),
                    "evidence": "TLS handshake succeeded",
                }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "check": "tls",
            "status": "fail",
            "target": f"{host}:{port}",
            "latency_ms": latency_ms,
            "evidence": f"TLS handshake failed: {exc}",
        }


def http_check(url: str, timeout_seconds: float = 2.0) -> dict:
    started = time.perf_counter()

    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            status_code = response.getcode()

            return {
                "check": "http",
                "status": "pass" if 200 <= status_code < 400 else "fail",
                "target": url,
                "http_status": status_code,
                "latency_ms": latency_ms,
                "evidence": f"HTTP response returned {status_code}",
            }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "check": "http",
            "status": "fail",
            "target": url,
            "latency_ms": latency_ms,
            "evidence": f"HTTP request failed: {exc}",
        }


def latency_budget_check(observed_ms: float, budget_ms: float) -> dict:
    return {
        "check": "latency_budget",
        "status": "pass" if observed_ms <= budget_ms else "fail",
        "observed_ms": observed_ms,
        "budget_ms": budget_ms,
        "evidence": (
            f"latency {observed_ms}ms within {budget_ms}ms budget"
            if observed_ms <= budget_ms
            else f"latency {observed_ms}ms exceeded {budget_ms}ms budget"
        ),
    }


def dependency_health_check(name: str, reachable: bool, latency_ms: float) -> dict:
    return {
        "check": "dependency_health",
        "status": "pass" if reachable else "fail",
        "dependency": name,
        "reachable": reachable,
        "latency_ms": latency_ms,
        "evidence": (
            f"{name} dependency reachable"
            if reachable
            else f"{name} dependency unreachable"
        ),
    }
