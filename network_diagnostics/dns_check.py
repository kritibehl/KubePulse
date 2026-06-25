import socket
from network_diagnostics.checks import result


def run_dns_check(host: str) -> dict:
    try:
        ip = socket.gethostbyname(host)
        return result("dns_resolution", "pass", host, f"{host} resolved to {ip}")
    except Exception as e:
        return result("dns_resolution", "fail", host, f"DNS resolution failed: {e}")
