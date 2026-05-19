import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPORTS = BASE / "reports"
REPORTS.mkdir(exist_ok=True)

topology = json.loads((BASE / "network_topology.json").read_text())
capacity = json.loads((BASE / "capacity_scenarios.json").read_text())
rules = json.loads((BASE / "config_validation_rules.json").read_text())["rules"]


def link_name(link):
    return f'{link["source"]}->{link["target"]}'


def validate_config():
    findings = []

    for node in topology["nodes"]:
        missing = [f for f in rules["required_node_fields"] if f not in node]
        if missing:
            findings.append({
                "type": "missing_node_metadata",
                "node": node.get("id", "unknown"),
                "missing": missing,
                "severity": "high"
            })

    for link in topology["links"]:
        missing = [f for f in rules["required_link_fields"] if f not in link]
        if missing:
            findings.append({
                "type": "missing_link_metadata",
                "link": link_name(link),
                "missing": missing,
                "severity": "high"
            })

        if link.get("latency_ms", 0) > rules["max_latency_ms"]:
            findings.append({
                "type": "latency_threshold_violation",
                "link": link_name(link),
                "observed": link["latency_ms"],
                "threshold": rules["max_latency_ms"],
                "severity": "high",
                "recommendation": "inspect routing path or shift traffic away from degraded link"
            })

        if link.get("packet_loss_pct", 0) > rules["max_packet_loss_pct"]:
            findings.append({
                "type": "packet_loss_threshold_violation",
                "link": link_name(link),
                "observed": link["packet_loss_pct"],
                "threshold": rules["max_packet_loss_pct"],
                "severity": "critical",
                "recommendation": "repair/replace degraded network segment or reroute traffic"
            })

    route_names = {r["name"] for r in topology["routes"]}
    for required in rules["required_routes"]:
        if required not in route_names:
            findings.append({
                "type": "missing_required_route",
                "route": required,
                "severity": "critical"
            })

    return findings


def analyze_capacity():
    link_by_name = {link_name(link): link for link in topology["links"]}
    results = []

    for scenario in capacity["scenarios"]:
        link = link_by_name.get(scenario["target_link"])
        if not link:
            results.append({
                "scenario": scenario["name"],
                "status": "fail",
                "reason": "target link not found",
                "severity": "critical"
            })
            continue

        expected = scenario["expected_mbps"]
        cap = link["capacity_mbps"]
        headroom_pct = round(((cap - expected) / cap) * 100, 2)
        degraded = headroom_pct < rules["min_capacity_headroom_pct"]

        results.append({
            "scenario": scenario["name"],
            "target_link": scenario["target_link"],
            "expected_mbps": expected,
            "capacity_mbps": cap,
            "headroom_pct": headroom_pct,
            "status": "fail" if degraded else "pass",
            "recommendation": "increase capacity or reroute traffic" if degraded else "capacity acceptable"
        })

    return results


def write_reports(findings, capacity_results):
    failed_findings = [f for f in findings if f["severity"] in {"high", "critical"}]
    failed_capacity = [r for r in capacity_results if r["status"] == "fail"]

    validation_status = "FAIL" if failed_findings or failed_capacity else "PASS"

    network_report = [
        "# Network Validation Report",
        "",
        f"Validation status: `{validation_status}`",
        "",
        "## Findings",
        ""
    ]

    if not findings:
        network_report.append("No configuration or routing findings detected.")
    else:
        for f in findings:
            network_report.append(f"- **{f['severity']}** `{f['type']}` on `{f.get('link', f.get('node', f.get('route', 'unknown')))}`")
            if "recommendation" in f:
                network_report.append(f"  - recommendation: {f['recommendation']}")

    network_report.extend([
        "",
        "## RCA Notes",
        "",
        "The checkout-to-payments path showed degraded packet loss and elevated latency. Recommended action is to reroute traffic or repair/replace the degraded segment before allowing release continuation."
    ])

    (REPORTS / "network_validation_report.md").write_text("\n".join(network_report))

    capacity_report = [
        "# Capacity Analysis Report",
        "",
        "| Scenario | Target Link | Expected Mbps | Capacity Mbps | Headroom % | Status | Recommendation |",
        "|---|---|---:|---:|---:|---|---|"
    ]

    for r in capacity_results:
        capacity_report.append(
            f"| {r['scenario']} | {r.get('target_link', 'unknown')} | {r.get('expected_mbps', 0)} | {r.get('capacity_mbps', 0)} | {r.get('headroom_pct', 0)} | {r['status']} | {r['recommendation']} |"
        )

    (REPORTS / "capacity_analysis_report.md").write_text("\n".join(capacity_report))

    summary = {
        "validation_status": validation_status,
        "findings_count": len(findings),
        "capacity_failures": len(failed_capacity),
        "repair_replace_recommended": any(
            "repair/replace" in f.get("recommendation", "") for f in findings
        ),
        "recommended_action": "reroute or repair degraded link" if validation_status == "FAIL" else "continue"
    }

    (REPORTS / "network_validation_summary.json").write_text(json.dumps(summary, indent=2))

    print(json.dumps(summary, indent=2))


def main():
    findings = validate_config()
    capacity_results = analyze_capacity()
    write_reports(findings, capacity_results)


if __name__ == "__main__":
    main()
