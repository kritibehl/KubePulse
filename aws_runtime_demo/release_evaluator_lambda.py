import json
from pathlib import Path

from s3_artifact_writer import s3_style_uri, write_release_artifact


def to_cloudwatch_payload(event: dict) -> dict:
    signals = event["signals"]

    return {
        "Namespace": "KubePulse/ReleaseSafety",
        "MetricData": [
            {
                "MetricName": "SafeToOperate",
                "Value": 1 if signals["safe_to_operate"] else 0,
                "Unit": "Count",
            },
            {
                "MetricName": "LatencyP95Ms",
                "Value": signals["p95_latency_ms"],
                "Unit": "Milliseconds",
            },
            {
                "MetricName": "LatencyP99Ms",
                "Value": signals["p99_latency_ms"],
                "Unit": "Milliseconds",
            },
            {
                "MetricName": "ErrorRate",
                "Value": signals["error_rate"],
                "Unit": "None",
            },
            {
                "MetricName": "DependencyRiskScore",
                "Value": signals["dependency_risk_score"],
                "Unit": "Count",
            },
        ],
    }


def evaluate_release(event: dict) -> dict:
    signals = event["signals"]

    reasons = []

    if signals["safe_to_operate"] is False:
        reasons.append("safe_to_operate_false")

    if signals["p95_latency_ms"] > 250:
        reasons.append("p95_latency_budget_violation")

    if signals["p99_latency_ms"] > 500:
        reasons.append("p99_latency_budget_violation")

    if signals["error_rate"] > 0.02:
        reasons.append("error_budget_violation")

    if signals["dependency_risk_score"] > 80:
        reasons.append("dependency_risk_threshold_violation")

    if signals["cloudwatch_alarm_state"] == "ALARM":
        reasons.append("cloudwatch_alarm_state_alarm")

    if signals["canary_validation"] != "pass":
        reasons.append("canary_validation_failed")

    blocked = bool(reasons)

    decision = {
        "deployment_id": event["deployment_id"],
        "site": event["site"],
        "wave": event["wave"],
        "release_decision": "block" if blocked else "continue",
        "rollback_required": blocked,
        "freeze_next_wave": blocked,
        "reasons": reasons,
    }

    return decision


def lambda_handler(event: dict, context=None) -> dict:
    decision = evaluate_release(event)
    metric_payload = to_cloudwatch_payload(event)

    decision_path = write_release_artifact(
        event["deployment_id"],
        "release_decision.json",
        decision,
    )

    metric_path = write_release_artifact(
        event["deployment_id"],
        "cloudwatch_metric_payload.json",
        metric_payload,
    )

    return {
        "decision": decision,
        "release_artifact_uri": s3_style_uri(decision_path),
        "metric_artifact_uri": s3_style_uri(metric_path),
    }


def main() -> None:
    event = json.loads(Path("aws_runtime_demo/sample_deployment_event.json").read_text())
    result = lambda_handler(event)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
