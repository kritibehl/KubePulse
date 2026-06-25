from network_diagnostics.checks import result


def run_latency_check(observed_ms: float, threshold_ms: float, target: str = "service") -> dict:
    if observed_ms <= threshold_ms:
        return result("latency", "pass", target, f"latency {observed_ms}ms within threshold {threshold_ms}ms", observed_ms)
    return result("latency", "fail", target, f"latency {observed_ms}ms exceeded threshold {threshold_ms}ms", observed_ms)


def run_packet_loss_check(packet_loss_pct: float, threshold_pct: float = 1.0, target: str = "service") -> dict:
    if packet_loss_pct <= threshold_pct:
        return result("packet_loss", "pass", target, f"packet loss {packet_loss_pct}% within threshold {threshold_pct}%")
    return result("packet_loss", "fail", target, f"packet loss {packet_loss_pct}% exceeded threshold {threshold_pct}%")
