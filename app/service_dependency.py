from __future__ import annotations

def infer_dependency_analysis(report: dict) -> dict:
    source = report.get("source_service", report.get("pod_name", "unknown-source"))
    target = report.get("target_service", "unknown-target")
    edges = report.get("dependency_edges") or [
        {"source": source, "target": target, "protocol": "http"},
        {"source": target, "target": "shared-db", "protocol": "tcp"},
    ]

    latency_error_propagation_path = [edge["source"] for edge in edges] + [edges[-1]["target"]]
    blast_radius_services = sorted({source, target, "shared-db", "frontend-gateway"})

    scenario = report.get("scenario", "unknown")
    if scenario == "dns_failure":
        likely_root_cause = "cluster DNS resolution path"
        impacted_segment = "service discovery"
    elif scenario in {"packet_loss", "tcp_resets", "connection_churn", "mtu_mismatch"}:
        likely_root_cause = f"{source}->{target} transport path"
        impacted_segment = "inter-service TCP path"
    elif scenario in {"node_partition", "dropped_egress", "degraded_ingress"}:
        likely_root_cause = "node or edge network segment"
        impacted_segment = "cross-node / ingress-egress network path"
    else:
        likely_root_cause = target
        impacted_segment = "upstream dependency path"

    return {
        "services": blast_radius_services,
        "edges": edges,
        "latency_error_propagation_path": latency_error_propagation_path,
        "blast_radius_services": blast_radius_services,
        "likely_root_cause": likely_root_cause,
        "impacted_network_segment": impacted_segment,
        "upstream_service": source,
        "downstream_service": target,
    }
