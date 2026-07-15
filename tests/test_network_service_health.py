from network_service_health.checks import (
    dependency_health_check,
    latency_budget_check,
)
from network_service_health.report import build_network_service_health_report


def test_latency_budget_failure_blocks_release():
    checks = [
        latency_budget_check(observed_ms=620, budget_ms=300),
    ]

    report = build_network_service_health_report(
        "orders-api",
        checks,
        "client -> proxy -> orders-api",
    )

    assert report["operate_decision"] == "unsafe_to_operate"
    assert report["release_decision"] == "block"


def test_dependency_failure_blocks_release():
    checks = [
        dependency_health_check(
            name="postgresql",
            reachable=False,
            latency_ms=920,
        )
    ]

    report = build_network_service_health_report(
        "orders-api",
        checks,
        "client -> proxy -> orders-api -> postgresql",
    )

    assert report["release_decision"] == "block"
    assert "downstream integration failure" in report["probable_root_causes"]


def test_all_checks_passing_allows_release():
    checks = [
        latency_budget_check(observed_ms=120, budget_ms=300),
        dependency_health_check(
            name="postgresql",
            reachable=True,
            latency_ms=25,
        ),
    ]

    report = build_network_service_health_report(
        "orders-api",
        checks,
        "client -> proxy -> orders-api -> postgresql",
    )

    assert report["operate_decision"] == "safe_to_operate"
    assert report["release_decision"] == "continue"
