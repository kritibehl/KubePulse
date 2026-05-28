import json
from pathlib import Path


QUALITY_CASES = [
    {
        "feature": "release_gate",
        "edge_case": "safe_to_operate_false",
        "expected_behavior": "block",
        "regression_risk": "high",
        "ci_status": "pass",
        "observed_decision": "block",
    },
    {
        "feature": "canary_rollout",
        "edge_case": "p95_latency_budget_violation",
        "expected_behavior": "block",
        "regression_risk": "high",
        "ci_status": "pass",
        "observed_decision": "block",
    },
    {
        "feature": "deployment_wave",
        "edge_case": "cloudwatch_alarm_state_alarm",
        "expected_behavior": "freeze_next_wave",
        "regression_risk": "high",
        "ci_status": "pass",
        "observed_decision": "freeze_next_wave",
    },
    {
        "feature": "security_gate",
        "edge_case": "missing_tls_and_auth",
        "expected_behavior": "block",
        "regression_risk": "critical",
        "ci_status": "pass",
        "observed_decision": "block",
    },
    {
        "feature": "capacity_gate",
        "edge_case": "p99_latency_budget_violation",
        "expected_behavior": "block",
        "regression_risk": "high",
        "ci_status": "pass",
        "observed_decision": "block",
    },
]


def evaluate_quality_matrix(cases=None):
    cases = cases or QUALITY_CASES
    results = []

    for case in cases:
        passed = (
            case["expected_behavior"] == case["observed_decision"]
            and case["ci_status"] == "pass"
        )

        results.append({
            **case,
            "quality_status": "pass" if passed else "fail",
            "release_block": case["observed_decision"] in {"block", "freeze_next_wave"},
        })

    return {
        "cases_total": len(results),
        "cases_passed": sum(1 for r in results if r["quality_status"] == "pass"),
        "cases_failed": sum(1 for r in results if r["quality_status"] == "fail"),
        "release_block_cases": sum(1 for r in results if r["release_block"]),
        "results": results,
    }


def main():
    report = evaluate_quality_matrix()

    out = Path("apple_quality_engineering/quality_matrix_report.json")
    out.write_text(json.dumps(report, indent=2))

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
