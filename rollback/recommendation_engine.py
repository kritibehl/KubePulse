from __future__ import annotations

import json
from pathlib import Path


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def recommend_rollback(canary: dict, topology: dict, alert: dict | None = None) -> dict:
    delta = canary.get("delta", {})
    candidate = canary.get("candidate", {})

    p95_regression = float(delta.get("p95_latency_regression_percent", 0))
    error_delta = float(delta.get("error_rate_delta", 0))
    safe_to_operate = bool(candidate.get("safe_to_operate", True))
    alert_triggered = bool((alert or {}).get("alert_triggered", False))

    impacted_services = topology.get("impacted_services", [])
    failure_root = topology.get("failure_root")

    reasons = []

    if p95_regression > 20:
        reasons.append("p95_latency_regression")

    if error_delta > 0.02:
        reasons.append("error_rate_budget_violation")

    if safe_to_operate is False:
        reasons.append("candidate_not_safe_to_operate")

    if alert_triggered:
        reasons.append("alert_triggered")

    if impacted_services:
        reasons.append("dependency_impact_detected")

    severity = "sev1" if len(impacted_services) >= 2 and alert_triggered else "sev2" if reasons else "sev3"

    rollback_recommended = bool(reasons) and safe_to_operate is False

    return {
        "release_id": canary.get("release_id"),
        "rollback_recommended": rollback_recommended,
        "release_decision": "block" if rollback_recommended else "continue",
        "blocked_rollout_reason": reasons,
        "rollback_candidate": "candidate_release" if rollback_recommended else None,
        "impacted_services": impacted_services,
        "failure_root": failure_root,
        "severity": severity,
        "signals": {
            "p95_latency_regression_percent": p95_regression,
            "error_rate_delta": error_delta,
            "safe_to_operate": safe_to_operate,
            "alert_triggered": alert_triggered,
        },
    }


def main() -> None:
    canary = load_json("canary/baseline_vs_candidate.json")
    topology = load_json("topology/dependency_graph.json")

    alert_path = Path("reports/alert_summary.json")
    alert = load_json(alert_path) if alert_path.exists() else {"alert_triggered": True}

    recommendation = recommend_rollback(canary, topology, alert)

    out_dir = Path("rollback")
    out_dir.mkdir(exist_ok=True)

    (out_dir / "rollback_recommendation.json").write_text(
        json.dumps(recommendation, indent=2)
    )

    print(json.dumps(recommendation, indent=2))


if __name__ == "__main__":
    main()
