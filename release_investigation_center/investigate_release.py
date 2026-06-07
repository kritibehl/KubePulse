import json
from pathlib import Path


def investigate(event):
    signals = event["signals"]

    root_causes = []

    if signals["dns_failures"] > 0:
        root_causes.append("dns_resolution_instability")
    if signals["tls_failures"] > 0:
        root_causes.append("tls_handshake_failures")
    if signals["packet_loss_percent"] > 2:
        root_causes.append("network_packet_loss")
    if signals["gpu_memory_pressure_percent"] > 80:
        root_causes.append("gpu_memory_pressure")
    if signals["token_latency_ms"] > 500:
        root_causes.append("ai_serving_latency_regression")
    if signals["dependency_risk_score"] > 80:
        root_causes.append("critical_dependency_degradation")

    affected = [
        d["service"] for d in event["dependencies"]
        if d["health"] in {"degraded", "critical", "impacted"}
    ]

    degraded_regions = [
        region for region, health in event["regions"].items()
        if health != "healthy"
    ]

    blast_radius = "high" if len(affected) >= 3 or degraded_regions else "medium"

    decision = {
        "deployment_id": event["deployment_id"],
        "likely_root_cause": root_causes[0] if root_causes else "unknown",
        "root_cause_candidates": root_causes,
        "affected_dependencies": affected,
        "degraded_regions": degraded_regions,
        "blast_radius": blast_radius,
        "rollback_recommendation": True,
        "freeze_next_wave": True,
        "release_decision": "block",
        "customer_impact": "high" if blast_radius == "high" else "medium"
    }

    return decision


def main():
    event = json.loads(Path("release_investigation_center/bad_deployment_event.json").read_text())
    decision = investigate(event)

    Path("release_investigation_center/reports/investigation_result.json").write_text(
        json.dumps(decision, indent=2)
    )

    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
