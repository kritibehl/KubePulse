def evaluate_thresholds(result: dict, scenario: dict) -> dict:
    thresholds = scenario.get("thresholds", {})

    recovery_window_max = thresholds.get("recovery_window_seconds_max")
    restart_count_max = thresholds.get("restart_count_max")
    readiness_false_positive_allowed = thresholds.get(
        "readiness_false_positive_allowed",
        False,
    )

    failures = []

    if (
        recovery_window_max is not None
        and result.get("recovery_window_seconds", 0.0) > recovery_window_max
    ):
        failures.append(
            f"Recovery window {result.get('recovery_window_seconds')}s exceeded "
            f"threshold {recovery_window_max}s."
        )

    if (
        restart_count_max is not None
        and result.get("restart_count", 0) > restart_count_max
    ):
        failures.append(
            f"Restart count {result.get('restart_count')} exceeded "
            f"threshold {restart_count_max}."
        )

    if (
        not readiness_false_positive_allowed
        and result.get("readiness_false_positive", False)
    ):
        failures.append(
            "Readiness false positive detected while scenario disallowed it."
        )

    if failures:
        result["status"] = "fail"
        result["pass_fail_reason"] = " ".join(failures)
        if result.get("readiness_false_positive", False):
            result["recommendation"] = (
                "Tighten readiness checks to better reflect degraded service state."
            )
        elif result.get("restart_count", 0) > 0:
            result["recommendation"] = (
                "Investigate restart behavior and probe stability under disruption."
            )
        else:
            result["recommendation"] = (
                "Review recovery behavior against scenario thresholds."
            )
    else:
        result["status"] = "pass"
        result["pass_fail_reason"] = "Scenario satisfied configured thresholds."
        result["recommendation"] = "No action required."

    return result
