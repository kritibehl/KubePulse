from app.chaos_injector import (
    inject_cpu_stress,
    inject_memory_stress,
)
from app.topology_decision_lab import run_topology_decision_scenario


def run_scenario_definition(scenario: dict) -> dict:
    scenario_type = scenario.get("type")
    target = scenario.get("target", {})
    execution = scenario.get("execution", {})

    pod_name = target.get("pod_name", "demo-app")
    namespace = target.get("namespace", "default")
    dry_run = execution.get("dry_run", True)

    if scenario_type == "cpu_stress":
        return inject_cpu_stress(
            pod_name=pod_name,
            namespace=namespace,
            dry_run=dry_run,
        )

    if scenario_type == "memory_stress":
        return inject_memory_stress(
            pod_name=pod_name,
            namespace=namespace,
            dry_run=dry_run,
        )

    if scenario_type == "readiness_false_positive":
        result = run_topology_decision_scenario("link_failure_failover")
        result["scenario"] = "readiness_false_positive"
        return result

    raise ValueError(f"Unsupported scenario type: {scenario_type}")
