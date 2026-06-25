import json
import sys
from pathlib import Path

try:
    from network_diagnostics.checks import classify_root_cause, remediation_for
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from network_diagnostics.checks import classify_root_cause, remediation_for


def build_report(incident: str, service: str, results: list[dict], expected_port: int = 5000) -> dict:
    root_cause = classify_root_cause(results)
    failed = [r for r in results if r["status"] == "fail"]

    return {
        "incident": incident,
        "service": service,
        "root_cause": root_cause,
        "status": "fail" if failed else "pass",
        "expected_port": expected_port,
        "evidence": results,
        "suggested_remediation": remediation_for(root_cause),
    }


def write_reports(report: dict) -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    json_path = reports_dir / "network_reachability_report.json"
    md_path = reports_dir / "network_reachability_report.md"
    failure_path = reports_dir / "service_connectivity_failure.md"
    remediation_path = reports_dir / "remediation_summary.md"

    json_path.write_text(json.dumps(report, indent=2))

    lines = [
        "# Network Reachability Report",
        "",
        f"Incident: {report['incident']}",
        f"Service: {report['service']}",
        f"Root cause: {report['root_cause']}",
        f"Status: {report['status']}",
        "",
        "## Evidence",
        "",
    ]

    for item in report["evidence"]:
        lines.append(f"- {item['name']}: {item['status'].upper()} — {item['evidence']}")

    lines += [
        "",
        "## Suggested Remediation",
        "",
        *[f"- {step}" for step in report["suggested_remediation"]],
        "",
    ]

    md_path.write_text("\n".join(lines))

    failure_path.write_text(
        "# Service Connectivity Failure\n\n"
        f"Incident: {report['incident']}\n\n"
        f"Root cause: {report['root_cause']}\n\n"
        "A service can be running but unreachable when DNS, TCP reachability, binding, HTTP health, latency, or dependency checks fail.\n"
    )

    remediation_path.write_text(
        "# Remediation Summary\n\n"
        + "\n".join(f"- {step}" for step in report["suggested_remediation"])
        + "\n"
    )


if __name__ == "__main__":
    demo_results = [
        {"name": "dns_resolution", "status": "pass", "target": "localhost", "evidence": "localhost resolved to 127.0.0.1", "latency_ms": 0.0},
        {"name": "tcp_reachability", "status": "fail", "target": "localhost:5000", "evidence": "TCP connection failed: connection refused", "latency_ms": 1.2},
        {"name": "http_health", "status": "fail", "target": "http://localhost:5000/health", "evidence": "HTTP health failed: connection refused", "latency_ms": 1.4},
        {"name": "latency", "status": "pass", "target": "localhost", "evidence": "latency 10ms within threshold 100ms", "latency_ms": 10.0},
        {"name": "dependency_reachability", "status": "fail", "target": "db:5432", "evidence": "dependency unreachable", "latency_ms": 0.0}
    ]
    report = build_report("Service unreachable", "edge-api", demo_results)
    write_reports(report)
    print(json.dumps(report, indent=2))
