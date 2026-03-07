import json
from pathlib import Path
from datetime import datetime


REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def save_report(report: dict) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    scenario = report.get("scenario", "unknown")
    pod_name = report.get("pod_name", "unknown-pod").replace("/", "-")
    filename = REPORTS_DIR / f"{scenario}_{pod_name}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return str(filename)


def list_reports() -> list[str]:
    return sorted(str(path) for path in REPORTS_DIR.glob("*.json"))


def read_report(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
