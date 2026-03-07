from app.chaos_injector import (
    inject_cpu_stress,
    inject_memory_stress,
    inject_readiness_false_positive,
)


def run_scenario_definition(scenario: dict) -> dict:
    scenario_type = scenario["type"]

    target = scenario.get("target", {})
    execution = scenario.get("execution", {})

    pod_name = target.get("pod_name", "demo-pod")
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
        return inject_readiness_false_positive(
            pod_name=pod_name,
            namespace=namespace,
            dry_run=dry_run,
        )

    raise ValueError(f"Unsupported scenario type: {scenario_type}")
