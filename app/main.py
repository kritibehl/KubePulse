from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app

from app.analytics_store import fetch_history, persist_report, trend_summary
from app.cache import cache_health
from app.dashboard_export import export_dashboard_dataset
from app.chaos_injector import (
    inject_cpu_stress,
    inject_memory_stress,
    inject_readiness_false_positive,
)
from app.db import init_db
from app.network_scenarios import (
    inject_connection_churn,
    inject_degraded_ingress,
    inject_dns_failure,
    inject_dropped_egress,
    inject_mtu_mismatch,
    inject_node_partition,
    inject_packet_loss,
    inject_service_latency,
    inject_tcp_resets,
)
from app.network_score import compute_network_health_score
from app.remediation_engine import recommend_network_remediation
from app.report_exporter import export_report_markdown
from app.report_store import list_reports, read_report, save_report
from app.resilience_score import compute_resilience_score
from app.scenario_loader import list_scenarios, load_scenario
from app.scenario_runner import run_scenario_definition
from app.schemas import HistoricalScenarioRequest, NetworkScenarioRequest, ResilienceReport, ScenarioRequest
from app.service_dependency import infer_dependency_analysis
from app.statistics_engine import compare_baseline_vs_degraded

app = FastAPI(title="KubePulse")
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
def startup() -> None:
    init_db()

def _finalize_result(result: dict) -> dict:
    result.update(compute_resilience_score(result))
    result.update(compute_network_health_score(result))
    dependency_analysis = infer_dependency_analysis(result)
    result.update(dependency_analysis)
    remediation = recommend_network_remediation(result, dependency_analysis)
    result.update(remediation)
    result["recommendation"] = f"{remediation['recommended_action']} | {remediation['suggested_config_change']}"
    report_path = save_report(result)
    result["report_path"] = report_path
    run_id = persist_report(result)
    result["run_id"] = run_id
    return result

def _network_response(builder, request: NetworkScenarioRequest) -> ResilienceReport:
    result = builder(
        namespace=request.namespace,
        source_service=request.source_service,
        target_service=request.target_service,
        dry_run=request.dry_run,
        run_group=request.run_group,
        run_kind=request.run_kind,
    )
    result = _finalize_result(result)
    return ResilienceReport(**result)

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "cache": cache_health()}

@app.get("/scenarios")
def get_scenarios() -> dict:
    return {"scenarios": list_scenarios()}

@app.get("/network/scenarios")
def get_network_scenarios() -> dict:
    return {
        "network_scenarios": [
            "packet_loss",
            "dns_failure",
            "service_latency",
            "node_partition",
            "dropped_egress",
            "degraded_ingress",
            "mtu_mismatch",
            "tcp_resets",
            "connection_churn",
        ]
    }

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
        result = _finalize_result(result)
        return ResilienceReport(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scenarios/run/{name}/record", response_model=ResilienceReport)
def run_scenario_with_group(name: str, request: HistoricalScenarioRequest) -> ResilienceReport:
    try:
        scenario = load_scenario(name)
        scenario["target"] = {"pod_name": request.pod_name, "namespace": request.namespace}
        scenario["execution"] = {"dry_run": request.dry_run}
        result = run_scenario_definition(scenario)
        result["run_group"] = request.run_group
        result["run_kind"] = request.run_kind
        result = _finalize_result(result)
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
        result = _finalize_result(result)
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
        result = _finalize_result(result)
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
        result = _finalize_result(result)
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/network/packet-loss", response_model=ResilienceReport)
def network_packet_loss(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_packet_loss, request)

@app.post("/network/dns-failure", response_model=ResilienceReport)
def network_dns_failure(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_dns_failure, request)

@app.post("/network/service-latency", response_model=ResilienceReport)
def network_service_latency(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_service_latency, request)

@app.post("/network/node-partition", response_model=ResilienceReport)
def network_node_partition(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_node_partition, request)

@app.post("/network/dropped-egress", response_model=ResilienceReport)
def network_dropped_egress(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_dropped_egress, request)

@app.post("/network/degraded-ingress", response_model=ResilienceReport)
def network_degraded_ingress(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_degraded_ingress, request)

@app.post("/network/mtu-mismatch", response_model=ResilienceReport)
def network_mtu_mismatch(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_mtu_mismatch, request)

@app.post("/network/tcp-resets", response_model=ResilienceReport)
def network_tcp_resets(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_tcp_resets, request)

@app.post("/network/connection-churn", response_model=ResilienceReport)
def network_connection_churn(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_connection_churn, request)

@app.post("/analysis/dependency-path")
def dependency_path_analysis(request: NetworkScenarioRequest) -> dict:
    synthetic_report = {
        "scenario": "dependency_path_analysis",
        "pod_name": request.source_service,
        "namespace": request.namespace,
        "source_service": request.source_service,
        "target_service": request.target_service,
        "dependency_edges": [
            {"source": request.source_service, "target": request.target_service, "protocol": "http"},
            {"source": request.target_service, "target": "shared-db", "protocol": "tcp"},
        ],
    }
    return infer_dependency_analysis(synthetic_report)

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
    return {"source_report": latest, "export_path": export_path}

@app.get("/scorecard/latest")
def get_latest_scorecard() -> dict:
    reports = list_reports()
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")
    latest = read_report(reports[-1])
    return latest

@app.get("/scorecards")
def get_scorecards() -> dict:
    reports = list_reports()
    return {"scorecards": [read_report(report_path) for report_path in reports]}

@app.get("/analytics/history")
def get_history(scenario: str | None = None, limit: int = 100) -> dict:
    return {"history": fetch_history(scenario=scenario, limit=limit)}

@app.get("/analytics/trends")
def get_trends() -> dict:
    return trend_summary()

@app.get("/analytics/statistics/{scenario}")
def get_statistics(scenario: str, run_group: str | None = None) -> dict:
    return compare_baseline_vs_degraded(scenario=scenario, run_group=run_group)

@app.get("/analytics/export/dashboard")
def export_dashboard() -> dict:
    export_path = export_dashboard_dataset()
    return {"export_path": export_path}
