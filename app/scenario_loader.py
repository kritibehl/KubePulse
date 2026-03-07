import yaml
from pathlib import Path


def load_scenario(name: str):
    path = Path("scenarios") / f"{name}.yaml"
    if not path.exists():
        raise ValueError(f"Scenario {name} not found")

    with open(path) as f:
        return yaml.safe_load(f)
