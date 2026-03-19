REQUIRED_FIELDS = [
    "scenario",
    "started_at",
    "ended_at",
    "status",
    "recovery_window_seconds",
    "latency_p95_ms",
    "error_rate",
]

NETWORK_REQUIRED_FIELDS = [
    "dns_success_rate",
    "tcp_connect_latency_ms",
    "http_success_rate",
    "path_recovery_time_seconds",
]

NETWORK_SCENARIOS = {
    "packet_loss",
    "dns_failure",
    "service_latency",
    "node_partition",
    "dropped_egress",
    "degraded_ingress",
    "mtu_mismatch",
    "tcp_resets",
    "connection_churn",
}

def assess_report_integrity(report: dict) -> dict:
    missing_fields = [field for field in REQUIRED_FIELDS if report.get(field) in (None, "", [])]
    warnings = []

    if report.get("scenario") in NETWORK_SCENARIOS:
        missing_fields.extend([field for field in NETWORK_REQUIRED_FIELDS if report.get(field) in (None, "", [])])

    if report.get("probe_mismatch") and report.get("readiness_after") == "ready":
        warnings.append("Probe mismatch detected while readiness remained ready.")
    if report.get("baseline_latency_p95_ms", 0.0) == 0.0 and report.get("observed_latency_p95_ms", 0.0) > 0.0:
        warnings.append("Observed latency exists but baseline probe data is missing.")
    if report.get("latency_p95_ms", 0.0) == 0.0 and report.get("error_rate", 0.0) == 0.0:
        warnings.append("Metrics look sparse; verify probe collection completed.")
    if report.get("scenario") in NETWORK_SCENARIOS and report.get("dns_success_rate", 1.0) < 0.9 and not report.get("probable_source_of_degradation"):
        warnings.append("DNS degradation present without root-cause attribution.")
    if report.get("scenario") in NETWORK_SCENARIOS and report.get("tcp_connect_latency_ms", 0.0) == 0.0:
        warnings.append("TCP connect latency missing for network scenario.")

    deduped_missing = sorted(set(missing_fields))

    if len(deduped_missing) >= 3:
        validity_status = "invalid"
    elif deduped_missing or warnings:
        validity_status = "partial"
    else:
        validity_status = "valid"

    confidence_score = max(0.1, round(1.0 - (0.12 * len(deduped_missing)) - (0.06 * len(warnings)), 2))
    notes = "; ".join(warnings) if warnings else "Sufficient data captured for reporting."

    return {
        "validity_status": validity_status,
        "confidence_score": confidence_score,
        "missing_fields": deduped_missing,
        "data_sufficiency_notes": notes,
    }
