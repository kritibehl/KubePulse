import json
from pathlib import Path


def build_network_service_health_report(
    service: str,
    checks: list[dict],
    proxy_path: str,
) -> dict:
    failed_checks = [check for check in checks if check["status"] == "fail"]

    if failed_checks:
        operate_decision = "unsafe_to_operate"
        release_decision = "block"
    else:
        operate_decision = "safe_to_operate"
        release_decision = "continue"

    probable_root_causes = []

    for check in failed_checks:
        mapping = {
            "dns": "DNS resolution or service discovery failure",
            "tcp": "closed port, firewall rule, bind-address issue, or unreachable host",
            "tls": "TLS handshake, certificate, protocol, or secure-listener failure",
            "http": "application route, proxy upstream, or service-health failure",
            "latency_budget": "performance degradation or overloaded dependency",
            "dependency_health": "downstream integration failure",
        }
        probable_root_causes.append(mapping.get(check["check"], "unknown failure"))

    return {
        "service": service,
        "proxy_style_reachability_path": proxy_path,
        "checks": checks,
        "failed_checks": len(failed_checks),
        "probable_root_causes": probable_root_causes,
        "operate_decision": operate_decision,
        "release_decision": release_decision,
        "recommended_escalation": (
            "escalate to service, network, or dependency owner based on failed layer"
            if failed_checks
            else "no escalation required"
        ),
    }


def write_reports(report: dict) -> None:
    reports = Path("reports")
    reports.mkdir(exist_ok=True)

    json_path = reports / "network_service_health_report.json"
    md_path = reports / "network_service_health_report.md"

    json_path.write_text(json.dumps(report, indent=2))

    lines = [
        "# Network Service Health Report",
        "",
        f"- Service: `{report['service']}`",
        f"- Proxy-style path: `{report['proxy_style_reachability_path']}`",
        f"- Operate decision: `{report['operate_decision']}`",
        f"- Release decision: `{report['release_decision']}`",
        "",
        "## Diagnostic Checklist",
        "",
        "| Check | Status | Evidence |",
        "|---|---|---|",
    ]

    for check in report["checks"]:
        lines.append(
            f"| {check['check']} | {check['status']} | {check.get('evidence', '')} |"
        )

    lines.extend([
        "",
        "## Probable Root Causes",
        "",
    ])

    if report["probable_root_causes"]:
        lines.extend(
            f"- {cause}" for cause in report["probable_root_causes"]
        )
    else:
        lines.append("- no failures detected")

    lines.extend([
        "",
        "## Incident Escalation",
        "",
        report["recommended_escalation"],
        "",
    ])

    md_path.write_text("\n".join(lines))


if __name__ == "__main__":
    sample_checks = [
        {
            "check": "dns",
            "status": "pass",
            "target": "service.internal",
            "evidence": "service.internal resolved to 10.0.1.15",
        },
        {
            "check": "tcp",
            "status": "pass",
            "target": "service.internal:443",
            "latency_ms": 12.0,
            "evidence": "TCP connection succeeded",
        },
        {
            "check": "tls",
            "status": "pass",
            "target": "service.internal:443",
            "latency_ms": 18.0,
            "evidence": "TLS handshake succeeded",
        },
        {
            "check": "http",
            "status": "pass",
            "target": "https://service.internal/health",
            "http_status": 200,
            "latency_ms": 620.0,
            "evidence": "HTTP response returned 200",
        },
        {
            "check": "latency_budget",
            "status": "fail",
            "observed_ms": 620.0,
            "budget_ms": 300.0,
            "evidence": "latency 620ms exceeded 300ms budget",
        },
        {
            "check": "dependency_health",
            "status": "fail",
            "dependency": "postgresql",
            "reachable": False,
            "latency_ms": 920.0,
            "evidence": "postgresql dependency unreachable",
        },
    ]

    report = build_network_service_health_report(
        service="orders-api",
        checks=sample_checks,
        proxy_path="client -> ingress/proxy -> orders-api -> postgresql",
    )
    write_reports(report)
    print(json.dumps(report, indent=2))
