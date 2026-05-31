import json
from pathlib import Path


def classify_incident(signal: dict) -> dict:
    latency_pct = int(signal["latency"].replace("+", "").replace("%", ""))
    error_pct = int(signal["error_rate"].replace("+", "").replace("%", ""))

    sev1 = (
        latency_pct >= 200
        or error_pct >= 5
        or signal.get("dependency_health") == "critical"
        or signal.get("cloudwatch_alarm_state") == "ALARM"
    )

    decision = {
        "incident_id": signal["incident_id"],
        "severity": "sev1" if sev1 else "sev2",
        "owner": "release_engineering",
        "rollback": sev1,
        "freeze": sev1,
        "customer_impact": "high" if sev1 else "medium",
        "recommended_actions": [
            "freeze rollout",
            "rollback candidate release",
            "notify release engineering owner",
            "preserve release evidence",
            "rerun health validation after recovery"
        ] if sev1 else [
            "continue monitoring",
            "review release metrics"
        ]
    }

    return decision


def main():
    signal = json.loads(Path("incident_commander/sample_incident_signal.json").read_text())
    decision = classify_incident(signal)

    out = Path("incident_commander/incident_command_decision.json")
    out.write_text(json.dumps(decision, indent=2))

    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
