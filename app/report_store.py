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

    report_to_save = dict(report)
    report_to_save["report_path"] = str(filename)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report_to_save, f, indent=2)

    return str(filename)


def list_reports() -> list[str]:
    return [
        str(path)
        for path in sorted(
            REPORTS_DIR.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
        )
    ]


def read_report(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
