from fastapi import FastAPI, HTTPException

from app.chaos_injector import inject_cpu_stress, inject_memory_stress
from app.report_store import list_reports, read_report, save_report
from app.schemas import ResilienceReport, ScenarioRequest

app = FastAPI(title="KubePulse")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/scenarios/cpu-stress", response_model=ResilienceReport)
def run_cpu_stress(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = inject_cpu_stress(
            pod_name=request.pod_name,
            namespace=request.namespace,
            dry_run=request.dry_run,
        )
        report_path = save_report(result)
        result["report_path"] = report_path
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/memory-stress", response_model=ResilienceReport)
def run_memory_stress(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = inject_memory_stress(
            pod_name=request.pod_name,
            namespace=request.namespace,
            dry_run=request.dry_run,
        )
        report_path = save_report(result)
        result["report_path"] = report_path
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports")
def get_reports() -> dict:
    return {"reports": list_reports()}


@app.get("/reports/latest")
def get_latest_report() -> dict:
    reports = list_reports()
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")

    latest = reports[-1]
    return read_report(latest)


@app.get("/scorecard/latest")
def get_latest_scorecard() -> dict:
    reports = list_reports()
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")

    latest = read_report(reports[-1])
    return {
        "scenario": latest["scenario"],
        "status": latest["status"],
        "recovery_window_seconds": latest["recovery_window_seconds"],
        "restart_count": latest["restart_count"],
        "probe_mismatch": latest["probe_mismatch"],
        "readiness_false_positive": latest.get("readiness_false_positive", False),
        "report_path": latest.get("report_path"),
    }


@app.get("/scorecards")
def get_scorecards() -> dict:
    reports = list_reports()
    scorecards = []

    for report_path in reports:
        report = read_report(report_path)
        scorecards.append(
            {
                "scenario": report["scenario"],
                "status": report["status"],
                "recovery_window_seconds": report["recovery_window_seconds"],
                "restart_count": report["restart_count"],
                "probe_mismatch": report["probe_mismatch"],
                "readiness_false_positive": report.get("readiness_false_positive", False),
                "report_path": report.get("report_path", report_path),
                "started_at": report["started_at"],
            }
        )

    return {"scorecards": scorecards}