from __future__ import annotations

def build_dependency_path_report(report: dict) -> dict:
    corr = report.get("path_trace_correlation") or {}
    latency_deltas = corr.get("latency_deltas", [])
    first_degraded_metric = None
    degraded_hop = report.get("degraded_hop")

    if latency_deltas:
        worst = max(latency_deltas, key=lambda x: x.get("delta_ms", 0.0))
        first_degraded_metric = {
            "hop": worst.get("hop"),
            "delta_ms": worst.get("delta_ms"),
        }

    return {
        "dependency_path_report": {
            "first_degraded_component": report.get("broken_hop") or degraded_hop,
            "first_degraded_metric": first_degraded_metric,
            "propagation_path": {
                "before": report.get("baseline_path"),
                "after": report.get("final_path"),
            },
            "likely_dominant_bottleneck": degraded_hop,
        }
    }
