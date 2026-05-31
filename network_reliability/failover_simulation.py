import json
from pathlib import Path


def simulate_failover(data):
    failed = data["failed_region"]
    required = data["required_failover_capacity_percent"]

    healthy_regions = {
        region: meta
        for region, meta in data["regions"].items()
        if region != failed and meta["status"] == "healthy"
    }

    total_remaining_capacity = sum(r["capacity_percent"] for r in healthy_regions.values())
    traffic_shifted = total_remaining_capacity >= required

    return {
        "failed_region": failed,
        "healthy_regions": list(healthy_regions.keys()),
        "traffic_shifted": traffic_shifted,
        "remaining_capacity": "safe" if traffic_shifted else "insufficient",
        "customer_impact": "minimal" if traffic_shifted else "high",
        "release_decision": "continue_with_failover" if traffic_shifted else "block"
    }


def main():
    data = json.loads(Path("network_reliability/multi_region_failover.json").read_text())
    report = simulate_failover(data)

    out = Path("network_reliability/reports/failover_report.json")
    out.write_text(json.dumps(report, indent=2))

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
