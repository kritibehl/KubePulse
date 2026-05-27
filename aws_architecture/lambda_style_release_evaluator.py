import json
from pathlib import Path


def evaluate(event: dict) -> dict:
    events = event.get("events", [])
    signals = event.get("signals", {})

    alarm_triggered = any(
        e.get("type") == "cloudwatch_alarm" and e.get("state") == "ALARM"
        for e in events
    )
    canary_failed = any(
        e.get("type") == "canary_validation" and e.get("status") == "fail"
        for e in events
    )
    rollback_triggered = any(
        e.get("type") == "rollback_gate" and e.get("status") == "triggered"
        for e in events
    )

    unsafe = (
        signals.get("safe_to_operate") is False
        or signals.get("p95_latency_ms", 0) > 250
        or signals.get("error_rate", 0) > 0.02
        or signals.get("dependency_risk_score", 0) > 80
        or alarm_triggered
        or canary_failed
        or rollback_triggered
    )

    reasons = []
    if alarm_triggered:
        reasons.append("cloudwatch_alarm_triggered")
    if canary_failed:
        reasons.append("canary_validation_failed")
    if rollback_triggered:
        reasons.append("rollback_gate_triggered")
    if signals.get("p95_latency_ms", 0) > 250:
        reasons.append("p95_latency_budget_violation")
    if signals.get("error_rate", 0) > 0.02:
        reasons.append("error_budget_violation")
    if signals.get("dependency_risk_score", 0) > 80:
        reasons.append("dependency_risk_threshold_violation")

    return {
        "deployment_id": event["deployment_id"],
        "site": event["site"],
        "release_decision": "block" if unsafe else "continue",
        "safe_to_operate": not unsafe,
        "freeze_next_wave": unsafe,
        "rollback_required": unsafe,
        "reasons": reasons,
    }


def main() -> None:
    event = json.loads(Path("aws_architecture/deployment_event.json").read_text())
    decision = evaluate(event)

    out = Path("aws_architecture/lambda_release_decision.json")
    out.write_text(json.dumps(decision, indent=2))

    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
