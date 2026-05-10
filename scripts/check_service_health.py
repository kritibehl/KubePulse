import json
from pathlib import Path

METRICS_PATH = Path("labs/ai_server_platform_validation/artifacts/release_decision.json")

def main() -> int:
    data = json.loads(METRICS_PATH.read_text())

    safe = data.get("safe_to_operate")
    decision = data.get("release_decision")
    regression = float(data.get("p95_regression_percent", data.get("latency_p95_delta_pct", 0)))

    alert = safe is False or decision == "block" or regression > 20

    result = {
        "service": "kubepulse",
        "alert_triggered": alert,
        "threshold_violated": "p95_latency_regression" if regression > 20 else None,
        "probable_cause": "latency regression exceeded release threshold" if alert else "within threshold",
        "recommended_remediation": "rollback_candidate_release" if alert else "continue_monitoring",
        "runbook_link": "ops/incident_response_runbook.md",
        "status": "detected" if alert else "healthy",
        "release_decision": decision,
        "safe_to_operate": safe,
        "p95_regression_percent": regression
    }

    print(json.dumps(result, indent=2))
    return 1 if alert else 0

if __name__ == "__main__":
    raise SystemExit(main())
