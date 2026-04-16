from __future__ import annotations
import json
from pathlib import Path

def build_decision_report(report: dict) -> dict:
    decision = {
        "scenario": report.get("scenario"),
        "probes_healthy": report.get("probes_say_healthy"),
        "service_available": bool((report.get("availability_achieved_pct", report.get("availability_achieved_pct_simulated", 0.0))) > 0),
        "slo_met": report.get("slo_met"),
        "downstream_healthy": report.get("status") != "fail",
        "error_rate_acceptable": float(report.get("error_rate_achieved_pct", report.get("error_rate", 0.0) * 100.0)) <= float(report.get("slo_error_rate_target", 1.0)),
        "safe_to_operate": report.get("safe_to_operate"),
        "recommendation": report.get("release_decision") or "hold",
        "key_metrics": {
            "convergence_seconds": report.get("convergence_seconds", 0.0),
            "degraded_path_requests_total": report.get("degraded_path_requests_total", 0),
            "unreachable_window_seconds": report.get("unreachable_window_seconds", 0.0),
            "path_changes_total": report.get("path_changes_total", 0),
            "latency_p95_ms": report.get("latency_p95_ms", 0.0),
            "latency_p99_ms": report.get("latency_p99_ms", 0.0),
        },
        "what_probes_missed": report.get("what_probes_missed", []),
    }
    out = Path("artifacts/reports/decision_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(decision, indent=2))
    return {"decision_report": decision, "decision_report_path": str(out)}
