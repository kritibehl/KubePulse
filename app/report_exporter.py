from pathlib import Path
from app.report_store import read_report


EXPORTS_DIR = Path("exports")
EXPORTS_DIR.mkdir(exist_ok=True)


def export_report_markdown(report_path: str) -> str:
    report = read_report(report_path)

    scenario = report.get("scenario", "unknown")
    started_at = report.get("started_at", "unknown")
    status = report.get("status", "unknown")
    recovery_window_seconds = report.get("recovery_window_seconds", 0.0)
    restart_count = report.get("restart_count", 0)
    probe_mismatch = report.get("probe_mismatch", False)
    readiness_false_positive = report.get("readiness_false_positive", False)
    readiness_before = report.get("readiness_before", "unknown")
    readiness_after = report.get("readiness_after", "unknown")
    pass_fail_reason = report.get(
        "pass_fail_reason",
        "No validation reason available.",
    )
    recommendation = report.get(
        "recommendation",
        "No recommendation available.",
    )
    stdout = report.get("stdout", "")
    stderr = report.get("stderr", "")
    source_report_path = report.get("report_path", report_path)

    markdown = f"""# KubePulse Resilience Report

## Scenario
- **Scenario:** {scenario}
- **Started At:** {started_at}
- **Status:** {status}

## Scorecard
- **Recovery Window (s):** {recovery_window_seconds}
- **Restart Count:** {restart_count}
- **Probe Mismatch:** {probe_mismatch}
- **Readiness False Positive:** {readiness_false_positive}

## Readiness Signals
- **Readiness Before:** {readiness_before}
- **Readiness After:** {readiness_after}

## Validation
- **Reason:** {pass_fail_reason}
- **Recommendation:** {recommendation}

## Execution Output
### stdout

    {stdout}

### stderr

    {stderr}

## Artifact
- **Source Report:** {source_report_path}
"""

    filename = EXPORTS_DIR / f"{Path(report_path).stem}.md"
    filename.write_text(markdown, encoding="utf-8")
    return str(filename)
