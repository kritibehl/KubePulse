import csv
from pathlib import Path
from sqlalchemy import select
from app.db import get_db_session
from app.models import (
    LatencyErrorSummary,
    NetworkHealthHistory,
    RecoveryWindowHistory,
    ScenarioRun,
    ScoreHistory,
)

def export_dashboard_dataset(path: str = "exports/dashboard_dataset.csv") -> str:
    output = Path(path)
    output.parent.mkdir(exist_ok=True)

    with get_db_session() as session:
        rows = session.execute(
            select(
                ScenarioRun.run_id,
                ScenarioRun.scenario,
                ScenarioRun.run_group,
                ScenarioRun.run_kind,
                ScenarioRun.status,
                ScenarioRun.validity_status,
                ScenarioRun.confidence_score,
                ScenarioRun.created_at,
                ScenarioRun.recommendation,
                ScoreHistory.resilience_score,
                ScoreHistory.slo_met,
                ScoreHistory.slo_availability_target,
                ScoreHistory.slo_latency_p99_target_ms,
                ScoreHistory.slo_error_rate_target,
                ScoreHistory.availability_achieved_pct,
                ScoreHistory.latency_p99_achieved_ms,
                ScoreHistory.error_rate_achieved_pct,
                ScoreHistory.error_budget_remaining_pct,
                RecoveryWindowHistory.recovery_window_seconds,
                RecoveryWindowHistory.restart_count,
                RecoveryWindowHistory.readiness_false_positive,
                LatencyErrorSummary.latency_p95_ms,
                LatencyErrorSummary.latency_p95_drift_pct,
                LatencyErrorSummary.error_rate,
                LatencyErrorSummary.error_rate_delta,
                NetworkHealthHistory.network_health_score,
                NetworkHealthHistory.dns_success_rate,
                NetworkHealthHistory.tcp_connect_latency_ms,
                NetworkHealthHistory.http_success_rate,
                NetworkHealthHistory.cross_zone_degradation_pct,
                NetworkHealthHistory.path_recovery_time_seconds,
                NetworkHealthHistory.network_availability_gap_pct,
            )
            .join(ScoreHistory, ScoreHistory.run_id == ScenarioRun.run_id)
            .join(RecoveryWindowHistory, RecoveryWindowHistory.run_id == ScenarioRun.run_id)
            .join(LatencyErrorSummary, LatencyErrorSummary.run_id == ScenarioRun.run_id)
            .join(NetworkHealthHistory, NetworkHealthHistory.run_id == ScenarioRun.run_id)
            .order_by(ScenarioRun.created_at.asc())
        ).all()

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "run_id", "scenario", "run_group", "run_kind", "status", "validity_status",
            "confidence_score", "created_at", "recommendation", "resilience_score",
            "slo_met", "slo_availability_target", "slo_latency_p99_target_ms",
            "slo_error_rate_target", "availability_achieved_pct", "latency_p99_achieved_ms",
            "error_rate_achieved_pct", "error_budget_remaining_pct",
            "recovery_window_seconds", "restart_count", "readiness_false_positive",
            "latency_p95_ms", "latency_p95_drift_pct", "error_rate", "error_rate_delta",
            "network_health_score", "dns_success_rate", "tcp_connect_latency_ms",
            "http_success_rate", "cross_zone_degradation_pct", "path_recovery_time_seconds",
            "network_availability_gap_pct"
        ])
        for row in rows:
            writer.writerow(list(row))
    return str(output)
