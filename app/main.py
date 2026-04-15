from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app

from app.analytics_store import fetch_history, persist_report, trend_summary
from app.cache import cache_health
from app.dashboard_export import export_dashboard_dataset
from app.ai_service_scenarios import run_ai_service_scenario
from app.topology_decision_lab import run_topology_decision_scenario
from app.path_trace_correlation import correlate_path_trace
from reports.scenario_summary import build_resilience_explanation
from reports.decision_report import build_decision_report
from reports.compare_view import build_compare_view
from validators.dependency_path import build_dependency_path_report
from validators.probe_analysis import build_probe_gap
from validators.assertions import evaluate_assertions
from validators.thresholds import evaluate_thresholds
from app.chaos_injector import (
    inject_cpu_stress,
    inject_memory_stress,
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
from app.multi_service_scenario import run_multi_service_failure
from app.remediation_engine import recommend_network_remediation
from app.report_exporter import export_report_markdown
from app.report_store import list_reports, read_report, save_report
from app.resilience_score import compute_resilience_score
from app.scenario_loader import list_scenarios, load_scenario
from app.scenario_runner import run_scenario_definition
from app.schemas import HistoricalScenarioRequest, NetworkScenarioRequest, ResilienceReport, ScenarioRequest
from app.service_dependency import infer_dependency_analysis
from app.slo_evaluator import evaluate_slo
from app.statistics_engine import compare_baseline_vs_degraded
from pathlib import Path
from validators.rollout_risk import compute_rollout_risk
from app.remediation_planner import build_remediation_plan
from reports.operator_action_plan import build_operator_action_plan
from app.plugin_registry import get_plugin, list_plugins
from app.operator_dashboard import build_operator_dashboard
from app.regression_compare import compare_baseline_candidate
from app.release_validation_matrix import VALIDATION_MATRIX
from app.kpi_budget_engine import evaluate_kpi_budgets
from app.release_decision_engine import classify_release_decision

app = FastAPI(title="KubePulse")



metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
def startup() -> None:
    init_db()

def _finalize_result(result: dict) -> dict:
    result.update(compute_resilience_score(result))
    result.update(compute_network_health_score(result))
    result.update(evaluate_slo(result))
    if result.get("baseline_path") or result.get("final_path"):
        result.update(correlate_path_trace(result))
    scenario_spec = {}
    scenario_file = Path("scenarios") / f"{result.get('scenario')}.yaml"
    if scenario_file.exists():
        import yaml
        scenario_spec = yaml.safe_load(scenario_file.read_text()) or {}
    result.update(build_compare_view(result))
    result.update(build_probe_gap(result))
    result.update(build_dependency_path_report(result))
    result.update(evaluate_thresholds(result, scenario_spec))
    result.update(build_resilience_explanation(result))
    result["safe_to_operate"] = bool(
        result.get("availability_ok", False)
        and result.get("p95_ok", False)
        and result.get("p99_ok", False)
        and result.get("error_rate_ok", False)
        and result.get("slo_met", False)
        and not result.get("readiness_false_positive", False)
    )
    result["probes_say_healthy"] = bool(result.get("readiness_before") == "ready")
    if not result.get("recommendation_action"):
        result["recommendation_action"] = (
            "continue" if result["safe_to_operate"]
            else ("block" if result.get("status") == "fail" else "reroute")
        )
    result.update(build_decision_report(result))
    dependency_analysis = infer_dependency_analysis(result)
    result.update(dependency_analysis)
    remediation = recommend_network_remediation(result, dependency_analysis)
    result.update(remediation)
    result["recommendation"] = f"{remediation['recommendation_action']} | {remediation['suggested_config_change']}"
    report_path = save_report(result)
    result["report_path"] = report_path
    run_id = persist_report(result)
    result["run_id"] = run_id
    rollout_risk = compute_rollout_risk(result)
    remediation_plan = build_remediation_plan(result, rollout_risk)
    operator_action_plan = build_operator_action_plan(result, rollout_risk, remediation_plan)

    result["rollout_risk"] = rollout_risk
    result["remediation_plan"] = remediation_plan
    result["operator_action_plan"] = operator_action_plan
    result["deployment_decision"] = remediation_plan.get("deployment_decision")

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





@app.post("/scenarios/readiness-false-positive", response_model=ResilienceReport)
def run_readiness_false_positive() -> ResilienceReport:
    result = run_topology_decision_scenario("link_failure_failover")
    result["scenario"] = "readiness_false_positive"
    result["slo"] = {}
    result = _finalize_result(result)
    return ResilienceReport(**result)

@app.post("/topology/link-failure-failover", response_model=ResilienceReport)
def topology_link_failure_failover(request: ScenarioRequest) -> ResilienceReport:
    result = run_topology_decision_scenario("link_failure_failover")
    result["slo"] = load_scenario("link_failure_failover").get("slo", {})
    result = _finalize_result(result)
    return ResilienceReport(**result)

@app.post("/topology/blackhole", response_model=ResilienceReport)
def topology_blackhole(request: ScenarioRequest) -> ResilienceReport:
    result = run_topology_decision_scenario("blackhole")
    result["slo"] = load_scenario("blackhole").get("slo", {})
    result = _finalize_result(result)
    return ResilienceReport(**result)

@app.post("/topology/asymmetric-path", response_model=ResilienceReport)
def topology_asymmetric_path(request: ScenarioRequest) -> ResilienceReport:
    result = run_topology_decision_scenario("asymmetric_path")
    result["slo"] = load_scenario("asymmetric_path").get("slo", {})
    result = _finalize_result(result)
    return ResilienceReport(**result)

@app.post("/topology/link-flap", response_model=ResilienceReport)
def topology_link_flap(request: ScenarioRequest) -> ResilienceReport:
    result = run_topology_decision_scenario("link_flap")
    result["slo"] = load_scenario("link_flap").get("slo", {})
    result = _finalize_result(result)
    return ResilienceReport(**result)

@app.post("/ai/model-inference-timeout", response_model=ResilienceReport)
def ai_model_inference_timeout(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = run_ai_service_scenario("model_inference_timeout", request.pod_name, request.namespace, request.dry_run)
        result["slo"] = load_scenario("model_inference_timeout").get("slo", {})
        result["ai_quality"] = load_scenario("model_inference_timeout").get("ai_quality", {})
        result = _finalize_result(result)
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/vector-db-degraded-latency", response_model=ResilienceReport)
def ai_vector_db_degraded_latency(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = run_ai_service_scenario("vector_db_degraded_latency", request.pod_name, request.namespace, request.dry_run)
        result["slo"] = load_scenario("vector_db_degraded_latency").get("slo", {})
        result["ai_quality"] = load_scenario("vector_db_degraded_latency").get("ai_quality", {})
        result = _finalize_result(result)
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/embedding-service-unavailable", response_model=ResilienceReport)
def ai_embedding_service_unavailable(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = run_ai_service_scenario("embedding_service_unavailable", request.pod_name, request.namespace, request.dry_run)
        result["slo"] = load_scenario("embedding_service_unavailable").get("slo", {})
        result["ai_quality"] = load_scenario("embedding_service_unavailable").get("ai_quality", {})
        result = _finalize_result(result)
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/tool-router-dependency-failure", response_model=ResilienceReport)
def ai_tool_router_dependency_failure(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = run_ai_service_scenario("tool_router_dependency_failure", request.pod_name, request.namespace, request.dry_run)
        result["slo"] = load_scenario("tool_router_dependency_failure").get("slo", {})
        result["ai_quality"] = load_scenario("tool_router_dependency_failure").get("ai_quality", {})
        result = _finalize_result(result)
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/partial-fallback-under-load", response_model=ResilienceReport)
def ai_partial_fallback_under_load(request: ScenarioRequest) -> ResilienceReport:
    try:
        result = run_ai_service_scenario("partial_fallback_under_load", request.pod_name, request.namespace, request.dry_run)
        result["slo"] = load_scenario("partial_fallback_under_load").get("slo", {})
        result["ai_quality"] = load_scenario("partial_fallback_under_load").get("ai_quality", {})
        result = _finalize_result(result)
        return ResilienceReport(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/network/connection-churn", response_model=ResilienceReport)
def network_connection_churn(request: NetworkScenarioRequest) -> ResilienceReport:
    return _network_response(inject_connection_churn, request)





@app.post("/scenarios/multi-service-cascade", response_model=ResilienceReport)
def multi_service_cascade() -> ResilienceReport:
    result = run_multi_service_failure()
    result = _finalize_result(result)
    result["safe_to_operate"] = False
    result["recommendation_action"] = "block"
    result["recommendation"] = "block | Dependency latency propagation detected. Investigate downstream service before rollout."
    return ResilienceReport(**result)

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


@app.get("/plugins")
def get_plugins() -> dict:
    return {"plugins": list_plugins()}

@app.get("/release-validation-matrix")
def get_release_validation_matrix() -> dict:
    return {"items": VALIDATION_MATRIX}

@app.post("/plugins/run/{name}", response_model=ResilienceReport)
def run_plugin_scenario(name: str) -> ResilienceReport:
    result = get_plugin(name).run()
    result.update({
        "run_id": result.get("run_id") or name,
        "pod_name": "network-lab",
        "namespace": "default",
        "started_at": result.get("started_at") or "2026-04-15T00:00:00+00:00",
        "ended_at": result.get("ended_at") or "2026-04-15T00:00:05+00:00",
        "success": False,
        "status": "fail",
        "restart_count": 0,
        "recovery_window_seconds": 5.0,
        "baseline_latency_p50_ms": 90.0,
        "baseline_latency_p95_ms": 180.0,
        "baseline_latency_p99_ms": 320.0,
        "baseline_error_rate": 0.0,
        "observed_latency_p50_ms": result.get("latency_p50_ms", 0.0),
        "observed_latency_p95_ms": result.get("latency_p95_ms", 0.0),
        "observed_latency_p99_ms": result.get("latency_p99_ms", 0.0),
        "observed_error_rate": result.get("error_rate", 0.0),
        "latency_p50_drift_pct": round(((float(result.get("latency_p50_ms", 0.0)) - 90.0) / 90.0) * 100.0, 2),
        "latency_p95_drift_pct": round(((float(result.get("latency_p95_ms", 0.0)) - 180.0) / 180.0) * 100.0, 2),
        "latency_p99_drift_pct": round(((float(result.get("latency_p99_ms", 0.0)) - 320.0) / 320.0) * 100.0, 2),
        "error_rate_delta": round(float(result.get("error_rate", 0.0)) - 0.0, 4),
        "pass_fail_reason": f"Plugin scenario {name} violated stable operating assumptions.",
        "safe_to_operate": False,
        "probes_say_healthy": True,
        "recommendation_action": "block",
        "recommendation": "block | Investigate plugin-triggered degradation before rollout.",
    })
    result.update(evaluate_kpi_budgets(result))
    result.update(classify_release_decision(result))
    result = _finalize_result(result)
    result["safe_to_operate"] = False
    result["recommendation_action"] = "block"
    result["recommendation"] = "block | Investigate plugin-triggered degradation before rollout."
    return ResilienceReport(**result)

@app.post("/compare/baseline-vs-candidate")
def compare_baseline_candidate_route() -> dict:
    baseline = {
        "latency_p95_ms": 180.0,
        "latency_p99_ms": 320.0,
        "error_rate": 0.01,
        "recovery_window_seconds": 4.0,
    }
    candidate = {
        "latency_p95_ms": 540.0,
        "latency_p99_ms": 880.0,
        "error_rate": 0.04,
        "recovery_window_seconds": 11.0,
    }
    return compare_baseline_candidate(baseline, candidate)

@app.post("/dashboard/operator")
def operator_dashboard_route() -> dict:
    report = run_multi_service_failure()
    report = _finalize_result(report)
    report["safe_to_operate"] = False
    report["recommendation_action"] = "block"
    report["recommendation"] = "block | Dependency latency propagation detected. Investigate downstream service before rollout."
    return build_operator_dashboard(report)

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
