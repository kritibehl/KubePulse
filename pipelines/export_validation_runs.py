import json
from pathlib import Path
from datetime import datetime, timezone

SOURCE_DIR = Path("labs/network_reliability")
OUT_DIR = Path("reports/validation_runs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

rows = []

for path in sorted(SOURCE_DIR.glob("*_report.json")):
    with path.open() as f:
        report = json.load(f)

    rows.append({
        "scenario": report.get("scenario"),
        "failure_class": report.get("failure_class"),
        "probes_say_healthy": report.get("probes_say_healthy"),
        "safe_to_operate": report.get("safe_to_operate"),
        "release_decision": report.get("release_decision"),
        "reason": report.get("reason"),
        "latency_p95_drift_pct": report.get("latency_p95_drift_pct"),
        "latency_p99_drift_pct": report.get("latency_p99_drift_pct"),
        "error_rate_delta": report.get("error_rate_delta"),
        "recovery_window_seconds": report.get("recovery_window_seconds"),
        "source_artifact": str(path)
    })

artifact = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "validation_run_count": len(rows),
    "validation_runs": rows
}

out_path = OUT_DIR / "validation_run_table.json"
with out_path.open("w") as f:
    json.dump(artifact, f, indent=2)

print(json.dumps(artifact, indent=2))
print(f"\nWrote {out_path}")
