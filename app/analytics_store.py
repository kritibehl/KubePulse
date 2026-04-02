from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Integer, func, select
from app.cache import set_latest_run_for_scenario
from app.data_quality import assess_report_integrity
from app.db import get_db_session
from app.models import (
    LatencyErrorSummary,
    NetworkHealthHistory,
    RecoveryWindowHistory,
    ScenarioRun,
    ScoreHistory,
)

def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def persist_report(report: dict) -> str:
    quality = assess_report_integrity(report)
    run_id = report.get("run_id") or uuid4().hex
    report["run_id"] = run_id
    report["validity_status"] = quality["validity_status"]
    report["confidence_score"] = quality["confidence_score"]
    report["missing_fields"] = quality["missing_fields"]
    report["data_sufficiency_notes"] = quality["data_sufficiency_notes"]

    with get_db_session() as session:
        session.add(
            ScenarioRun(
                run_id=run_id,
                scenario=report["scenario"],
                pod_name=report.get("pod_name", "unknown"),
                namespace=report.get("namespace", "default"),
                disruption_type=report.get("disruption_type", report.get("scenario", "unknown")),
                run_group=report.get("run_group"),
                run_kind=report.get("run_kind"),
                started_at=_parse_dt(report["started_at"]),
                ended_at=_parse_dt(report["ended_at"]),
                success=bool(report.get("success", False)),
                status=report.get("status", "fail"),
                recommendation=report.get("recommendation", ""),
                report_path=report.get("report_path"),
                validity_status=quality["validity_status"],
                confidence_score=quality["confidence_score"],
                data_sufficiency_notes=quality["data_sufficiency_notes"],
                missing_fields=",".join(quality["missing_fields"]),
                created_at=datetime.now(timezone.utc),
            )
        )
        session.flush()
        session.add(
            ScoreHistory(
                run_id=run_id,
                resilience_score=int(report.get("resilience_score", 0)),
                recovery_score=int(report.get("recovery_score", 0)),
                latency_score=int(report.get("latency_score", 0)),
                error_score=int(report.get("error_score", 0)),
                probe_integrity_score=int(report.get("probe_integrity_score", 0)),
                slo_availability_target=float(report.get("slo_availability_target", 99.5)),
                slo_latency_p99_target_ms=float(report.get("slo_latency_p99_target_ms", 500.0)),
                slo_error_rate_target=float(report.get("slo_error_rate_target", 1.0)),
                slo_window_minutes=int(report.get("slo_window_minutes", 30)),
                availability_achieved_pct=float(report.get("availability_achieved_pct", 0.0)),
                latency_p99_achieved_ms=float(report.get("latency_p99_achieved_ms", 0.0)),
                error_rate_achieved_pct=float(report.get("error_rate_achieved_pct", 0.0)),
                error_budget_remaining_pct=float(report.get("error_budget_remaining_pct", 0.0)),
                slo_met=bool(report.get("slo_met", False)),
            )
        )
        session.add(
            RecoveryWindowHistory(
                run_id=run_id,
                recovery_window_seconds=float(report.get("recovery_window_seconds", 0.0)),
                restart_count=int(report.get("restart_count", 0)),
                readiness_false_positive=bool(report.get("readiness_false_positive", False)),
                probe_mismatch=bool(report.get("probe_mismatch", False)),
            )
        )
        session.add(
            LatencyErrorSummary(
                run_id=run_id,
                latency_p50_ms=float(report.get("latency_p50_ms", 0.0)),
                latency_p95_ms=float(report.get("latency_p95_ms", 0.0)),
                latency_p99_ms=float(report.get("latency_p99_ms", 0.0)),
                error_rate=float(report.get("error_rate", 0.0)),
                baseline_latency_p50_ms=float(report.get("baseline_latency_p50_ms", 0.0)),
                baseline_latency_p95_ms=float(report.get("baseline_latency_p95_ms", 0.0)),
                baseline_latency_p99_ms=float(report.get("baseline_latency_p99_ms", 0.0)),
                baseline_error_rate=float(report.get("baseline_error_rate", 0.0)),
                observed_latency_p50_ms=float(report.get("observed_latency_p50_ms", 0.0)),
                observed_latency_p95_ms=float(report.get("observed_latency_p95_ms", 0.0)),
                observed_latency_p99_ms=float(report.get("observed_latency_p99_ms", 0.0)),
                observed_error_rate=float(report.get("observed_error_rate", 0.0)),
                latency_p50_drift_pct=float(report.get("latency_p50_drift_pct", 0.0)),
                latency_p95_drift_pct=float(report.get("latency_p95_drift_pct", 0.0)),
                latency_p99_drift_pct=float(report.get("latency_p99_drift_pct", 0.0)),
                error_rate_delta=float(report.get("error_rate_delta", 0.0)),
            )
        )
        session.add(
            NetworkHealthHistory(
                run_id=run_id,
                network_health_score=int(report.get("network_health_score", 0)),
                dns_success_rate=float(report.get("dns_success_rate", 1.0)),
                tcp_connect_latency_ms=float(report.get("tcp_connect_latency_ms", 0.0)),
                http_success_rate=float(report.get("http_success_rate", 1.0)),
                cross_zone_degradation_pct=float(report.get("cross_zone_degradation_pct", 0.0)),
                path_recovery_time_seconds=float(report.get("path_recovery_time_seconds", report.get("recovery_window_seconds", 0.0))),
                network_availability_gap_pct=float(report.get("network_availability_gap_pct", 0.0)),
                fallback_success_rate_pct=float(report.get("fallback_success_rate_pct", 0.0)),
                degraded_serving_mode=bool(report.get("degraded_serving_mode", False)),
                full_outage=bool(report.get("full_outage", False)),
            )
        )
    set_latest_run_for_scenario(report["scenario"], run_id)
    return run_id

def fetch_history(scenario: str | None = None, limit: int = 100) -> list[dict]:
    with get_db_session() as session:
        stmt = (
            select(
                ScenarioRun.run_id,
                ScenarioRun.scenario,
                ScenarioRun.run_group,
                ScenarioRun.run_kind,
                ScenarioRun.status,
                ScenarioRun.validity_status,
                ScenarioRun.confidence_score,
                ScenarioRun.created_at,
                ScoreHistory.resilience_score,
                ScoreHistory.slo_met,
                ScoreHistory.availability_achieved_pct,
                ScoreHistory.latency_p99_achieved_ms,
                ScoreHistory.error_rate_achieved_pct,
                ScoreHistory.error_budget_remaining_pct,
                RecoveryWindowHistory.recovery_window_seconds,
                RecoveryWindowHistory.readiness_false_positive,
                LatencyErrorSummary.latency_p95_ms,
                LatencyErrorSummary.error_rate,
                LatencyErrorSummary.latency_p95_drift_pct,
                LatencyErrorSummary.error_rate_delta,
                NetworkHealthHistory.network_health_score,
                NetworkHealthHistory.dns_success_rate,
                NetworkHealthHistory.tcp_connect_latency_ms,
                NetworkHealthHistory.http_success_rate,
                NetworkHealthHistory.fallback_success_rate_pct,
                NetworkHealthHistory.degraded_serving_mode,
                NetworkHealthHistory.full_outage,
            )
            .join(ScoreHistory, ScoreHistory.run_id == ScenarioRun.run_id)
            .join(RecoveryWindowHistory, RecoveryWindowHistory.run_id == ScenarioRun.run_id)
            .join(LatencyErrorSummary, LatencyErrorSummary.run_id == ScenarioRun.run_id)
            .join(NetworkHealthHistory, NetworkHealthHistory.run_id == ScenarioRun.run_id)
            .order_by(ScenarioRun.created_at.desc())
            .limit(limit)
        )
        if scenario:
            stmt = stmt.where(ScenarioRun.scenario == scenario)
        rows = session.execute(stmt).all()
        return [dict(row._mapping) for row in rows]

def trend_summary() -> dict:
    with get_db_session() as session:
        score_rows = session.execute(
            select(
                ScenarioRun.scenario,
                func.avg(ScoreHistory.resilience_score).label("avg_resilience_score"),
                func.avg(RecoveryWindowHistory.recovery_window_seconds).label("avg_recovery_window_seconds"),
                func.avg(LatencyErrorSummary.latency_p95_drift_pct).label("avg_latency_p95_drift_pct"),
                func.avg(LatencyErrorSummary.error_rate_delta).label("avg_error_rate_delta"),
                func.avg(NetworkHealthHistory.network_health_score).label("avg_network_health_score"),
                func.avg(NetworkHealthHistory.dns_success_rate).label("avg_dns_success_rate"),
                func.avg(NetworkHealthHistory.tcp_connect_latency_ms).label("avg_tcp_connect_latency_ms"),
                func.avg(NetworkHealthHistory.http_success_rate).label("avg_http_success_rate"),
                func.avg(NetworkHealthHistory.fallback_success_rate_pct).label("avg_fallback_success_rate_pct"),
                func.sum(func.cast(NetworkHealthHistory.degraded_serving_mode, Integer)).label("degraded_serving_count"),
                func.sum(func.cast(NetworkHealthHistory.full_outage, Integer)).label("full_outage_count"),
                func.avg(ScoreHistory.error_budget_remaining_pct).label("avg_error_budget_remaining_pct"),
                func.sum(func.cast(ScoreHistory.slo_met, Integer)).label("slo_met_count"),
                func.sum(func.cast(RecoveryWindowHistory.readiness_false_positive, Integer)).label("readiness_false_positive_count"),
            )
            .join(ScoreHistory, ScoreHistory.run_id == ScenarioRun.run_id)
            .join(RecoveryWindowHistory, RecoveryWindowHistory.run_id == ScenarioRun.run_id)
            .join(LatencyErrorSummary, LatencyErrorSummary.run_id == ScenarioRun.run_id)
            .join(NetworkHealthHistory, NetworkHealthHistory.run_id == ScenarioRun.run_id)
            .group_by(ScenarioRun.scenario)
            .order_by(ScenarioRun.scenario.asc())
        ).all()

        recommendation_rows = session.execute(
            select(ScenarioRun.recommendation, func.count().label("count"))
            .group_by(ScenarioRun.recommendation)
            .order_by(func.count().desc())
        ).all()

    return {
        "scenario_trends": [dict(row._mapping) for row in score_rows],
        "recommendation_distribution": [dict(row._mapping) for row in recommendation_rows],
    }
