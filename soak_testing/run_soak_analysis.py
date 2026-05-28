import json
from pathlib import Path


def analyze_soak(data: dict) -> dict:
    results = []

    for scenario in data["scenarios"]:
        latency_drift = scenario["latency_p95_end_ms"] - scenario["latency_p95_start_ms"]
        latency_drift_pct = round(
            (latency_drift / scenario["latency_p95_start_ms"]) * 100,
            2,
        )
        error_accumulation = scenario["error_count_end"] - scenario["error_count_start"]

        release_decision = "block" if (
            latency_drift_pct > 100
            or error_accumulation > 100
            or scenario["resource_pressure"] == "high"
        ) else "continue" if scenario["status"] == "pass" else "watch"

        results.append({
            "duration": scenario["duration"],
            "latency_drift_ms": latency_drift,
            "latency_drift_pct": latency_drift_pct,
            "error_accumulation": error_accumulation,
            "resource_pressure": scenario["resource_pressure"],
            "release_decision": release_decision,
        })

    return {
        "soak_runs": len(results),
        "blocked_runs": sum(1 for r in results if r["release_decision"] == "block"),
        "watch_runs": sum(1 for r in results if r["release_decision"] == "watch"),
        "results": results,
    }


def main() -> None:
    data = json.loads(Path("soak_testing/soak_scenarios.json").read_text())
    report = analyze_soak(data)

    out = Path("soak_testing/reports/soak_analysis_report.json")
    out.write_text(json.dumps(report, indent=2))

    lines = [
        "# Long-Running Soak Test Report",
        "",
        "| Duration | Latency Drift | Drift % | Error Accumulation | Resource Pressure | Decision |",
        "|---|---:|---:|---:|---|---|",
    ]

    for r in report["results"]:
        lines.append(
            f"| {r['duration']} | {r['latency_drift_ms']} ms | {r['latency_drift_pct']}% | {r['error_accumulation']} | {r['resource_pressure']} | {r['release_decision']} |"
        )

    Path("soak_testing/reports/soak_analysis_report.md").write_text("\n".join(lines))

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
