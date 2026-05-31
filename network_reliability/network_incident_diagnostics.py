import json
from pathlib import Path


def classify_incidents(data):
    results = []

    for item in data["incidents"]:
        severity = "sev1" if item["customer_impact"] == "high" or item["affected_services"] >= 8 else "sev2"

        results.append({
            "incident": item["incident"],
            "affected_services": item["affected_services"],
            "severity": severity,
            "customer_impact": item["customer_impact"],
            "rollback_required": item["rollback_required"],
            "owner": "network_reliability",
            "recommended_action": "rollback_or_failover" if item["rollback_required"] else "monitor"
        })

    return {
        "incidents_analyzed": len(results),
        "sev1_count": sum(1 for r in results if r["severity"] == "sev1"),
        "rollback_required_count": sum(1 for r in results if r["rollback_required"]),
        "results": results
    }


def main():
    data = json.loads(Path("network_reliability/network_incidents.json").read_text())
    report = classify_incidents(data)

    out = Path("network_reliability/reports/network_incident_report.json")
    out.write_text(json.dumps(report, indent=2))

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
