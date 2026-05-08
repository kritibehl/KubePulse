from pathlib import Path
import yaml


DEFAULT_CONFIG_PATH = Path("config/slo_config.yaml")


def load_slo_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    if not path.exists():
        return {
            "latency_budget_ms": {"p95": 250, "p99": 500},
            "error_rate_budget": 0.02,
            "recovery_time_budget_seconds": 10,
            "probe_mismatch_policy": {"block_on_false_green": True},
            "release_policy": {"rollback_review_on_block": True},
        }

    with path.open() as f:
        return yaml.safe_load(f)


def evaluate_slo_gate(result: dict, config: dict | None = None) -> dict:
    cfg = config or load_slo_config()
    violated = []

    p95 = float(result.get("latency_p95_ms", result.get("observed_latency_p95_ms", 0.0)) or 0.0)
    p99 = float(result.get("latency_p99_ms", result.get("observed_latency_p99_ms", 0.0)) or 0.0)
    error_rate = float(result.get("error_rate", result.get("observed_error_rate", 0.0)) or 0.0)
    recovery = float(result.get("recovery_window_seconds", result.get("recovery_time_seconds", 0.0)) or 0.0)

    if p95 > cfg["latency_budget_ms"]["p95"]:
        violated.append("p95_latency")
    if p99 > cfg["latency_budget_ms"]["p99"]:
        violated.append("p99_latency")
    if error_rate > cfg["error_rate_budget"]:
        violated.append("error_rate")
    if recovery > cfg["recovery_time_budget_seconds"]:
        violated.append("recovery_time")

    false_green = (
        result.get("probes_say_healthy") is True
        and result.get("safe_to_operate") is False
    )

    if cfg["probe_mismatch_policy"].get("block_on_false_green") and false_green:
        violated.append("probe_mismatch_false_green")

    blocked = bool(violated)

    return {
        "violated_budgets": violated,
        "rollback_review": blocked and cfg["release_policy"].get("rollback_review_on_block", True),
        "safe_to_operate": False if blocked else result.get("safe_to_operate", True),
        "release_decision": "block" if blocked else result.get("release_decision", "continue"),
    }
