from __future__ import annotations

from typing import Any


DEFAULT_POLICY = {
    # Project policy, not claimed as a universal SRE standard.
    "elevated_burn_rate": 1.0,
    "fast_burn_1h": 4.0,
    "fast_burn_6h": 2.0,
}


def _validate_counts(requests: int, errors: int) -> None:
    if requests <= 0:
        raise ValueError("requests must be greater than zero")

    if errors < 0:
        raise ValueError("errors cannot be negative")

    if errors > requests:
        raise ValueError("errors cannot exceed requests")


def _window_result(
    *,
    requests: int,
    errors: int,
    allowed_error_fraction: float,
) -> dict[str, Any]:
    _validate_counts(requests, errors)

    error_fraction = errors / requests
    availability_percent = (1.0 - error_fraction) * 100.0
    error_rate_percent = error_fraction * 100.0
    burn_rate = error_fraction / allowed_error_fraction

    return {
        "requests": requests,
        "errors": errors,
        "availability_percent": round(availability_percent, 6),
        "error_rate_percent": round(error_rate_percent, 6),
        "burn_rate": round(burn_rate, 6),
    }


def evaluate_error_budget(
    measurements: dict[str, Any],
    policy: dict[str, float] | None = None,
) -> dict[str, Any]:
    policy = policy or DEFAULT_POLICY

    slo_percent = float(
        measurements.get("availability_slo_percent", 99.9)
    )

    if not 0 < slo_percent < 100:
        raise ValueError(
            "availability_slo_percent must be between 0 and 100"
        )

    allowed_error_percent = 100.0 - slo_percent
    allowed_error_fraction = allowed_error_percent / 100.0

    cumulative = measurements["cumulative"]

    cumulative_requests = int(cumulative["requests"])
    cumulative_errors = int(cumulative["errors"])

    _validate_counts(
        cumulative_requests,
        cumulative_errors,
    )

    allowed_failures = (
        cumulative_requests * allowed_error_fraction
    )

    budget_consumed_percent = (
        cumulative_errors / allowed_failures
    ) * 100.0

    budget_remaining_percent = max(
        0.0,
        100.0 - budget_consumed_percent,
    )

    cumulative_availability = (
        1.0 - cumulative_errors / cumulative_requests
    ) * 100.0

    windows: dict[str, dict[str, Any]] = {}

    for window_name, values in measurements["windows"].items():
        windows[window_name] = _window_result(
            requests=int(values["requests"]),
            errors=int(values["errors"]),
            allowed_error_fraction=allowed_error_fraction,
        )

    burn_1h = windows.get("1h", {}).get("burn_rate", 0.0)
    burn_6h = windows.get("6h", {}).get("burn_rate", 0.0)

    max_burn_rate = max(
        (
            item["burn_rate"]
            for item in windows.values()
        ),
        default=0.0,
    )

    budget_exhausted = (
        budget_consumed_percent >= 100.0
    )

    fast_burn = (
        burn_1h >= policy["fast_burn_1h"]
        and burn_6h >= policy["fast_burn_6h"]
    )

    elevated = (
        max_burn_rate >= policy["elevated_burn_rate"]
    )

    if budget_exhausted:
        burn_status = "BUDGET_EXHAUSTED"
        release_action = "BLOCK"
        reason = "availability_error_budget_exhausted"

    elif fast_burn:
        burn_status = "FAST_BURN"
        release_action = "BLOCK"
        reason = "multi_window_fast_burn_detected"

    elif elevated:
        burn_status = "ELEVATED"
        release_action = "ALLOW_WITH_WARNING"
        reason = "error_budget_burn_elevated"

    else:
        burn_status = "NORMAL"
        release_action = "ALLOW"
        reason = "error_budget_burn_normal"

    return {
        "availability_slo_percent": slo_percent,
        "allowed_error_percent": round(
            allowed_error_percent,
            6,
        ),
        "cumulative": {
            "requests": cumulative_requests,
            "errors": cumulative_errors,
            "observed_availability_percent": round(
                cumulative_availability,
                6,
            ),
            "allowed_failures": round(
                allowed_failures,
                6,
            ),
            "budget_consumed_percent": round(
                budget_consumed_percent,
                6,
            ),
            "budget_remaining_percent": round(
                budget_remaining_percent,
                6,
            ),
            "budget_exhausted": budget_exhausted,
        },
        "windows": windows,
        "max_burn_rate": round(max_burn_rate, 6),
        "burn_status": burn_status,
        "release_action": release_action,
        "reason": reason,
        "policy": {
            "elevated_burn_rate": policy[
                "elevated_burn_rate"
            ],
            "fast_burn_1h": policy[
                "fast_burn_1h"
            ],
            "fast_burn_6h": policy[
                "fast_burn_6h"
            ],
        },
    }
