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
        result["report_path"] = "pending"
        report_path = save_report(result)
        result["report_path"] = report_path
        save_report(result)
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
        result["report_path"] = "pending"
        report_path = save_report(result)
        result["report_path"] = report_path
        save_report(result)
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