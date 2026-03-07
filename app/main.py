from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app

from app.chaos_injector import (
    inject_cpu_stress,
    inject_memory_stress,
    inject_readiness_false_positive,
)
from app.report_exporter import export_report_markdown
from app.report_store import list_reports, read_report, save_report
from app.resilience_score import compute_resilience_score
from app.scenario_loader import list_scenarios, load_scenario
from app.scenario_runner import run_scenario_definition
from app.schemas import ResilienceReport, ScenarioRequest

app = FastAPI(title="KubePulse")
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/scenarios")
def get_scenarios() -> dict:
    return {"scenarios": list_scenarios()}


@app.get("/scenarios/{name}")
def get_scenario(name: str) -> dict:
    try:
        return load_scenario(name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/scenarios/run/{name}", response_model=ResilienceReport)
def run_scenario_by_name(name: str) -> ResilienceReport:
    try:
        scenario = load_scenario(name)
        result = run_scenario_definition(scenario)
        result.update(compute_resilience_score(result))
        report_path = save_report(result)
        result["report_path"] = report_path
        return ResilienceReport(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/cpu-stress", response_model=ResilienceReport)
def run_cpu_stress(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = inject_cpu_stress(
            pod_name=request.pod_name,
            namespace=request.namespace,
            dry_run=request.dry_run,
        )
        result.update(compute_resilience_score(result))
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
        result.update(compute_resilience_score(result))
        report_path = save_report(result)
        result["report_path"] = report_path
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/readiness-false-positive", response_model=ResilienceReport)
def run_readiness_false_positive(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = inject_readiness_false_positive(
            pod_name=request.pod_name,
            namespace=request.namespace,
            dry_run=request.dry_run,
        )
        result.update(compute_resilience_score(result))
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


@app.get("/reports/export/latest")
def export_latest_report() -> dict:
    reports = list_reports()
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")
    latest = reports[-1]
    export_path = export_report_markdown(latest)
    return {
        "source_report": latest,
        "export_path": export_path,
    }


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
        "latency_p95_ms": latest.get("latency_p95_ms", 0.0),
        "error_rate": latest.get("error_rate", 0.0),
        "resilience_score": latest.get("resilience_score", 0),
        "recovery_score": latest.get("recovery_score", 0),
        "latency_score": latest.get("latency_score", 0),
        "error_score": latest.get("error_score", 0),
        "probe_integrity_score": latest.get("probe_integrity_score", 0),
        "pass_fail_reason": latest.get(
            "pass_fail_reason",
            "No validation reason available.",
        ),
        "recommendation": latest.get(
            "recommendation",
            "No recommendation available.",
        ),
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
                "readiness_false_positive": report.get(
                    "readiness_false_positive",
                    False,
                ),
                "latency_p95_ms": report.get("latency_p95_ms", 0.0),
                "error_rate": report.get("error_rate", 0.0),
                "resilience_score": report.get("resilience_score", 0),
                "recovery_score": report.get("recovery_score", 0),
                "latency_score": report.get("latency_score", 0),
                "error_score": report.get("error_score", 0),
                "probe_integrity_score": report.get("probe_integrity_score", 0),
                "pass_fail_reason": report.get(
                    "pass_fail_reason",
                    "No validation reason available.",
                ),
                "recommendation": report.get(
                    "recommendation",
                    "No recommendation available.",
                ),
                "report_path": report.get("report_path", report_path),
                "started_at": report["started_at"],
            }
        )

    return {"scorecards": scorecards}
