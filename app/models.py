from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class ScenarioRun(Base):
    __tablename__ = "scenario_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    scenario: Mapped[str] = mapped_column(String(128), index=True)
    pod_name: Mapped[str] = mapped_column(String(255))
    namespace: Mapped[str] = mapped_column(String(255))
    disruption_type: Mapped[str] = mapped_column(String(128), index=True)
    run_group: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    run_kind: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    success: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(String(32), index=True)
    recommendation: Mapped[str] = mapped_column(Text, default="")
    report_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    validity_status: Mapped[str] = mapped_column(String(32), index=True, default="valid")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    data_sufficiency_notes: Mapped[str] = mapped_column(Text, default="")
    missing_fields: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

class ScoreHistory(Base):
    __tablename__ = "score_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_runs.run_id"), index=True)
    resilience_score: Mapped[int] = mapped_column(Integer, default=0)
    recovery_score: Mapped[int] = mapped_column(Integer, default=0)
    latency_score: Mapped[int] = mapped_column(Integer, default=0)
    error_score: Mapped[int] = mapped_column(Integer, default=0)
    probe_integrity_score: Mapped[int] = mapped_column(Integer, default=0)

class RecoveryWindowHistory(Base):
    __tablename__ = "recovery_window_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_runs.run_id"), index=True)
    recovery_window_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    restart_count: Mapped[int] = mapped_column(Integer, default=0)
    readiness_false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    probe_mismatch: Mapped[bool] = mapped_column(Boolean, default=False)

class LatencyErrorSummary(Base):
    __tablename__ = "latency_error_summaries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_runs.run_id"), index=True)
    latency_p50_ms: Mapped[float] = mapped_column(Float, default=0.0)
    latency_p95_ms: Mapped[float] = mapped_column(Float, default=0.0)
    latency_p99_ms: Mapped[float] = mapped_column(Float, default=0.0)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    baseline_latency_p50_ms: Mapped[float] = mapped_column(Float, default=0.0)
    baseline_latency_p95_ms: Mapped[float] = mapped_column(Float, default=0.0)
    baseline_latency_p99_ms: Mapped[float] = mapped_column(Float, default=0.0)
    baseline_error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    observed_latency_p50_ms: Mapped[float] = mapped_column(Float, default=0.0)
    observed_latency_p95_ms: Mapped[float] = mapped_column(Float, default=0.0)
    observed_latency_p99_ms: Mapped[float] = mapped_column(Float, default=0.0)
    observed_error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    latency_p50_drift_pct: Mapped[float] = mapped_column(Float, default=0.0)
    latency_p95_drift_pct: Mapped[float] = mapped_column(Float, default=0.0)
    latency_p99_drift_pct: Mapped[float] = mapped_column(Float, default=0.0)
    error_rate_delta: Mapped[float] = mapped_column(Float, default=0.0)

class NetworkHealthHistory(Base):
    __tablename__ = "network_health_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_runs.run_id"), index=True)
    network_health_score: Mapped[int] = mapped_column(Integer, default=0)
    dns_success_rate: Mapped[float] = mapped_column(Float, default=1.0)
    tcp_connect_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    http_success_rate: Mapped[float] = mapped_column(Float, default=1.0)
    cross_zone_degradation_pct: Mapped[float] = mapped_column(Float, default=0.0)
    path_recovery_time_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    network_availability_gap_pct: Mapped[float] = mapped_column(Float, default=0.0)
