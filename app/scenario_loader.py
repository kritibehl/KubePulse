from pathlib import Path
import yaml


SCENARIOS_DIR = Path("scenarios")


def load_scenario(name: str) -> dict:
    scenario_path = SCENARIOS_DIR / f"{name}.yaml"
    if not scenario_path.exists():
        raise FileNotFoundError(f"Scenario '{name}' not found at {scenario_path}")

    with open(scenario_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def list_scenarios() -> list[str]:
    return sorted(path.stem for path in SCENARIOS_DIR.glob("*.yaml"))
