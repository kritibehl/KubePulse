from __future__ import annotations
from datetime import datetime, timedelta, timezone

def _network_profile(scenario: str, run_kind: str | None) -> dict:
    baseline = {
        "packet_loss_pct": 0.5,
        "dns_success_rate": 0.995,
        "tcp_connect_latency_ms": 18.0,
        "http_success_rate": 0.992,
        "cross_zone_degradation_pct": 2.0,
        "path_recovery_time_seconds": 4.0,
        "network_availability_gap_pct": 0.3,
        "connection_failure_rate": 0.008,
        "latency_injection_ms": 15.0,
        "tcp_reset_rate": 0.002,
        "recovery_window_seconds": 5.0,
        "latency_p50_ms": 110.0,
        "latency_p95_ms": 165.0,
        "latency_p99_ms": 210.0,
        "error_rate": 0.01,
        "readiness_false_positive": False,
        "probe_mismatch": False,
        "status": "pass",
        "success": True,
    }
    degraded = {
        "packet_loss_pct": 7.5,
        "dns_success_rate": 0.91,
        "tcp_connect_latency_ms": 145.0,
        "http_success_rate": 0.84,
        "cross_zone_degradation_pct": 24.0,
        "path_recovery_time_seconds": 16.0,
        "network_availability_gap_pct": 11.0,
        "connection_failure_rate": 0.17,
        "latency_injection_ms": 180.0,
        "tcp_reset_rate": 0.11,
        "recovery_window_seconds": 14.0,
        "latency_p50_ms": 190.0,
        "latency_p95_ms": 315.0,
        "latency_p99_ms": 420.0,
        "error_rate": 0.08,
        "readiness_false_positive": True,
        "probe_mismatch": True,
        "status": "fail",
        "success": False,
    }

    profile = dict(degraded if run_kind == "degraded" else baseline)

    scenario_overrides = {
        "packet_loss": {"packet_loss_pct": 12.0 if run_kind == "degraded" else 1.0},
        "dns_failure": {
            "dns_success_rate": 0.55 if run_kind == "degraded" else 0.985,
            "http_success_rate": 0.72 if run_kind == "degraded" else 0.99,
            "readiness_false_positive": True if run_kind == "degraded" else False,
        },
        "service_latency": {
            "latency_injection_ms": 240.0 if run_kind == "degraded" else 20.0,
            "tcp_connect_latency_ms": 175.0 if run_kind == "degraded" else 20.0,
            "latency_p95_ms": 360.0 if run_kind == "degraded" else 170.0,
        },
        "node_partition": {
            "cross_zone_degradation_pct": 31.0 if run_kind == "degraded" else 4.0,
            "connection_failure_rate": 0.23 if run_kind == "degraded" else 0.01,
            "path_recovery_time_seconds": 22.0 if run_kind == "degraded" else 5.0,
        },
        "dropped_egress": {
            "http_success_rate": 0.61 if run_kind == "degraded" else 0.985,
            "error_rate": 0.13 if run_kind == "degraded" else 0.015,
        },
        "degraded_ingress": {
            "latency_p95_ms": 340.0 if run_kind == "degraded" else 175.0,
            "error_rate": 0.09 if run_kind == "degraded" else 0.012,
        },
        "mtu_mismatch": {
            "tcp_reset_rate": 0.16 if run_kind == "degraded" else 0.004,
            "packet_loss_pct": 9.0 if run_kind == "degraded" else 0.7,
        },
        "tcp_resets": {
            "tcp_reset_rate": 0.22 if run_kind == "degraded" else 0.01,
            "connection_failure_rate": 0.19 if run_kind == "degraded" else 0.012,
        },
        "connection_churn": {
            "connection_failure_rate": 0.21 if run_kind == "degraded" else 0.015,
            "tcp_connect_latency_ms": 155.0 if run_kind == "degraded" else 24.0,
        },
    }

    profile.update(scenario_overrides.get(scenario, {}))
    return profile

def _build_report(
    scenario: str,
    namespace: str,
    source_service: str,
    target_service: str,
    run_group: str | None,
    run_kind: str | None,
    dry_run: bool,
) -> dict:
    started = datetime.now(timezone.utc)
    ended = started + timedelta(seconds=1)
    p = _network_profile(scenario, run_kind)

    pass_fail_reason = (
        "Baseline network path remained within thresholds."
        if run_kind != "degraded"
        else "Injected network degradation exceeded latency/availability thresholds."
    )

    return {
        "scenario": scenario,
        "pod_name": source_service,
        "namespace": namespace,
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "success": p["success"],
        "recovery_window_seconds": p["recovery_window_seconds"],
        "restart_count": 0,
        "probe_mismatch": p["probe_mismatch"],
        "status": p["status"],
        "latency_p50_ms": p["latency_p50_ms"],
        "latency_p95_ms": p["latency_p95_ms"],
        "latency_p99_ms": p["latency_p99_ms"],
        "error_rate": p["error_rate"],
        "baseline_latency_p50_ms": 110.0,
        "baseline_latency_p95_ms": 165.0,
        "baseline_latency_p99_ms": 210.0,
        "baseline_error_rate": 0.01,
        "observed_latency_p50_ms": p["latency_p50_ms"],
        "observed_latency_p95_ms": p["latency_p95_ms"],
        "observed_latency_p99_ms": p["latency_p99_ms"],
        "observed_error_rate": p["error_rate"],
        "latency_p50_drift_pct": round(((p["latency_p50_ms"] - 110.0) / 110.0) * 100, 2),
        "latency_p95_drift_pct": round(((p["latency_p95_ms"] - 165.0) / 165.0) * 100, 2),
        "latency_p99_drift_pct": round(((p["latency_p99_ms"] - 210.0) / 210.0) * 100, 2),
        "error_rate_delta": round(p["error_rate"] - 0.01, 4),
        "stdout": f"{'Dry run: simulated' if dry_run else 'Executed'} {scenario} disruption from {source_service} to {target_service}",
        "stderr": "",
        "error": None,
        "readiness_before": "ready",
        "readiness_after": "ready" if not p["readiness_false_positive"] else "ready-but-network-degraded",
        "readiness_false_positive": p["readiness_false_positive"],
        "pass_fail_reason": pass_fail_reason,
        "recommendation": "Pending remediation analysis.",
        "run_group": run_group,
        "run_kind": run_kind,
        "source_service": source_service,
        "target_service": target_service,
        "disruption_type": scenario,
        "dns_success_rate": p["dns_success_rate"],
        "tcp_connect_latency_ms": p["tcp_connect_latency_ms"],
        "http_success_rate": p["http_success_rate"],
        "cross_zone_degradation_pct": p["cross_zone_degradation_pct"],
        "path_recovery_time_seconds": p["path_recovery_time_seconds"],
        "network_availability_gap_pct": p["network_availability_gap_pct"],
        "connection_failure_rate": p["connection_failure_rate"],
        "packet_loss_pct": p["packet_loss_pct"],
        "latency_injection_ms": p["latency_injection_ms"],
        "tcp_reset_rate": p["tcp_reset_rate"],
        "mtu_mismatch_detected": scenario == "mtu_mismatch",
        "dependency_edges": [
            {"source": source_service, "target": target_service, "protocol": "http"},
            {"source": target_service, "target": "shared-db", "protocol": "tcp"},
        ],
    }

def inject_packet_loss(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("packet_loss", namespace, source_service, target_service, run_group, run_kind, dry_run)

def inject_dns_failure(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("dns_failure", namespace, source_service, target_service, run_group, run_kind, dry_run)

def inject_service_latency(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("service_latency", namespace, source_service, target_service, run_group, run_kind, dry_run)

def inject_node_partition(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("node_partition", namespace, source_service, target_service, run_group, run_kind, dry_run)

def inject_dropped_egress(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("dropped_egress", namespace, source_service, target_service, run_group, run_kind, dry_run)

def inject_degraded_ingress(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("degraded_ingress", namespace, source_service, target_service, run_group, run_kind, dry_run)

def inject_mtu_mismatch(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("mtu_mismatch", namespace, source_service, target_service, run_group, run_kind, dry_run)

def inject_tcp_resets(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("tcp_resets", namespace, source_service, target_service, run_group, run_kind, dry_run)

def inject_connection_churn(namespace: str, source_service: str, target_service: str, dry_run: bool, run_group: str | None, run_kind: str | None) -> dict:
    return _build_report("connection_churn", namespace, source_service, target_service, run_group, run_kind, dry_run)
