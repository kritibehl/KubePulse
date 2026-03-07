from pathlib import Path
import yaml

from app.scenario_loader import load_scenario
from app.scenario_runner import run_scenario_definition


def load_pack(name: str) -> dict:
    pack_path = Path("packs") / f"{name}.yaml"
    if not pack_path.exists():
        raise FileNotFoundError(f"Pack '{name}' not found at {pack_path}")

    with open(pack_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_pack(name: str) -> dict:
    pack = load_pack(name)
    results = []

    for scenario_name in pack.get("scenarios", []):
        scenario = load_scenario(scenario_name)
        result = run_scenario_definition(scenario)
        results.append(result)

    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "pass")
    failed = total - passed

    return {
        "pack": name,
        "total_scenarios": total,
        "passed": passed,
        "failed": failed,
        "results": results,
    }
