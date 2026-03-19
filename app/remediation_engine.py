from __future__ import annotations

def recommend_network_remediation(report: dict, dependency_analysis: dict) -> dict:
    scenario = report.get("scenario", "unknown")
    dns_success_rate = float(report.get("dns_success_rate", 1.0))
    tcp_connect_latency_ms = float(report.get("tcp_connect_latency_ms", 0.0))
    http_success_rate = float(report.get("http_success_rate", 1.0))
    readiness_false_positive = bool(report.get("readiness_false_positive", False))
    root_cause = dependency_analysis.get("likely_root_cause", "unknown")

    probable_source = root_cause
    action = "observe"
    rollback = "No rollback required."
    confidence = 0.62
    config_change = "No immediate config change."

    if scenario == "dns_failure" or dns_success_rate < 0.9:
        action = "reroute"
        rollback = "Rollback recent DNS policy or service-discovery changes."
        config_change = "Validate CoreDNS, stub domains, and service discovery policy."
        confidence = 0.88
    elif scenario in {"packet_loss", "mtu_mismatch", "tcp_resets", "connection_churn"}:
        action = "isolate"
        rollback = "Rollback recent network policy, MTU, or transport tuning changes."
        config_change = "Inspect CNI path, MTU alignment, and transport retries."
        confidence = 0.84
    elif scenario in {"degraded_ingress", "dropped_egress", "node_partition"}:
        action = "reroute"
        rollback = "Rollback ingress/egress policy or node-local networking changes."
        config_change = "Shift traffic away from impaired node/zone and verify network policy."
        confidence = 0.83
    elif tcp_connect_latency_ms > 120 or http_success_rate < 0.9:
        action = "scale"
        rollback = "Rollback recent capacity or routing changes."
        config_change = "Increase healthy replicas and reduce load on degraded path."
        confidence = 0.79

    if readiness_false_positive:
        config_change += " Tighten readiness probes to reflect real dependency availability."
        confidence = min(0.95, confidence + 0.05)

    return {
        "probable_source_of_degradation": probable_source,
        "recommended_action": action,
        "confidence": round(confidence, 2),
        "suggested_rollback": rollback,
        "suggested_config_change": config_change,
    }
