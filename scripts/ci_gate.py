import sys

from app.multi_service_scenario import run_multi_service_failure
from app.topology_decision_lab import run_topology_decision_scenario


def assert_gate(name: str, result: dict) -> None:
    print(f"\n=== {name} ===")
    print(f"scenario={result.get('scenario')}")
    print(f"readiness_false_positive={result.get('readiness_false_positive')}")
    print(f"probes_say_healthy={result.get('probes_say_healthy')}")
    print(f"safe_to_operate={result.get('safe_to_operate')}")
    print(f"recommendation_action={result.get('recommendation_action')}")
    print(f"pass_fail_reason={result.get('pass_fail_reason')}")

    if result.get("probes_say_healthy") and result.get("safe_to_operate"):
        raise SystemExit(
            f"{name} failed gate: probes are healthy but scenario was expected to be unsafe."
        )


def main() -> int:
    topo = run_topology_decision_scenario("link_failure_failover")
    topo["scenario"] = "readiness_false_positive"

    cascade = run_multi_service_failure()

    assert_gate("readiness_false_positive", topo)
    assert_gate("multi_service_cascade", cascade)

    print("\nCI gate checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
