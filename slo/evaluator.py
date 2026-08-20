from __future__ import annotations

from copy import deepcopy
from typing import Any


DEFAULT_SLOS = {
    "availability_percent": {
        "label": "Availability",
        "operator": ">=",
        "threshold": 99.9,
        "unit": "%",
    },
    "p95_latency_ms": {
        "label": "p95 latency",
        "operator": "<=",
        "threshold": 300.0,
        "unit": "ms",
    },
    "error_rate_percent": {
        "label": "Error rate",
        "operator": "<=",
        "threshold": 1.0,
        "unit": "%",
    },
    "recovery_time_seconds": {
        "label": "Recovery time",
        "operator": "<=",
        "threshold": 60.0,
        "unit": "seconds",
    },
}


def _passes(observed: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return observed >= threshold

    if operator == "<=":
        return observed <= threshold

    raise ValueError(f"Unsupported SLO operator: {operator}")


def evaluate_slos(
    observations: dict[str, Any],
    thresholds: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Evaluate release observations against KubePulse SLOs.

    Missing metrics fail closed because a production release should not
    be approved when required release-safety evidence is unavailable.
    """

    slos = deepcopy(thresholds or DEFAULT_SLOS)

    evaluations: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    for metric_name, slo in slos.items():
        raw_value = observations.get(metric_name)

        if raw_value is None:
            result = {
                "metric": metric_name,
                "label": slo["label"],
                "observed": None,
                "threshold": slo["threshold"],
                "operator": slo["operator"],
                "unit": slo["unit"],
                "status": "MISSING",
                "passed": False,
                "reason": "required_slo_metric_missing",
            }

            evaluations.append(result)
            violations.append(result)
            continue

        observed = float(raw_value)
        passed = _passes(
            observed,
            slo["operator"],
            float(slo["threshold"]),
        )

        result = {
            "metric": metric_name,
            "label": slo["label"],
            "observed": observed,
            "threshold": float(slo["threshold"]),
            "operator": slo["operator"],
            "unit": slo["unit"],
            "status": "PASS" if passed else "FAIL",
            "passed": passed,
        }

        evaluations.append(result)

        if not passed:
            violations.append(result)

    allowed = not violations

    return {
        "decision": "ALLOW" if allowed else "BLOCK",
        "safe_to_release": allowed,
        "slo_count": len(evaluations),
        "passed_slo_count": sum(
            1 for item in evaluations if item["passed"]
        ),
        "failed_slo_count": len(violations),
        "evaluations": evaluations,
        "violations": violations,
    }
