#!/usr/bin/env bash
set -euo pipefail

mkdir -p app scripts dashboards/powerbi exports

cat > requirements.txt <<'REQ'
fastapi
uvicorn
requests
prometheus-client
pyyaml
sqlalchemy
psycopg[binary]
scipy
redis
REQ

cat > docker-compose.yml <<'YAML'
version: "3.9"

services:
  kubepulse-db:
    image: postgres:16
    container_name: kubepulse-db
    environment:
      POSTGRES_DB: kubepulse
      POSTGRES_USER: kubepulse
      POSTGRES_PASSWORD: kubepulse
    ports:
      - "5432:5432"
    volumes:
      - kubepulse-pgdata:/var/lib/postgresql/data

  kubepulse-redis:
    image: redis:7
    container_name: kubepulse-redis
    ports:
      - "6379:6379"

volumes:
  kubepulse-pgdata:
YAML

cat > app/db.py <<'PY'
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kubepulse.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db() -> None:
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
PY

cat > app/models.py <<'PY'
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
PY

cat > app/data_quality.py <<'PY'
REQUIRED_FIELDS = [
    "scenario",
    "started_at",
    "ended_at",
    "status",
    "recovery_window_seconds",
    "latency_p95_ms",
    "error_rate",
]

def assess_report_integrity(report: dict) -> dict:
    missing_fields = [field for field in REQUIRED_FIELDS if report.get(field) in (None, "", [])]
    warnings = []

    if report.get("probe_mismatch") and report.get("readiness_after") == "ready":
        warnings.append("Probe mismatch detected while readiness remained ready.")
    if report.get("baseline_latency_p95_ms", 0.0) == 0.0 and report.get("observed_latency_p95_ms", 0.0) > 0.0:
        warnings.append("Observed latency exists but baseline probe data is missing.")
    if report.get("latency_p95_ms", 0.0) == 0.0 and report.get("error_rate", 0.0) == 0.0:
        warnings.append("Metrics look sparse; verify probe collection completed.")

    if len(missing_fields) >= 3:
        validity_status = "invalid"
    elif missing_fields or warnings:
        validity_status = "partial"
    else:
        validity_status = "valid"

    confidence_score = max(0.1, round(1.0 - (0.12 * len(missing_fields)) - (0.06 * len(warnings)), 2))
    notes = "; ".join(warnings) if warnings else "Sufficient data captured for reporting."

    return {
        "validity_status": validity_status,
        "confidence_score": confidence_score,
        "missing_fields": missing_fields,
        "data_sufficiency_notes": notes,
    }
PY

cat > app/cache.py <<'PY'
import os
try:
    import redis
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL")
_client = redis.from_url(REDIS_URL, decode_responses=True) if redis and REDIS_URL else None

def set_latest_run_for_scenario(scenario: str, run_id: str) -> None:
    if _client:
        _client.set(f"kubepulse:latest:{scenario}", run_id)

def cache_health() -> dict:
    if not _client:
        return {"enabled": False}
    try:
        return {"enabled": True, "ping": bool(_client.ping())}
    except Exception as exc:
        return {"enabled": True, "error": str(exc)}
PY

cat > app/analytics_store.py <<'PY'
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Integer, func, select
from app.cache import set_latest_run_for_scenario
from app.data_quality import assess_report_integrity
from app.db import get_db_session
from app.models import LatencyErrorSummary, RecoveryWindowHistory, ScenarioRun, ScoreHistory

def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def persist_report(report: dict) -> str:
    quality = assess_report_integrity(report)
    run_id = report.get("run_id") or uuid4().hex
    report["run_id"] = run_id

    with get_db_session() as session:
        session.add(
            ScenarioRun(
                run_id=run_id,
                scenario=report["scenario"],
                pod_name=report.get("pod_name", "unknown"),
                namespace=report.get("namespace", "default"),
                disruption_type=report.get("scenario", "unknown"),
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
        session.add(
            ScoreHistory(
                run_id=run_id,
                resilience_score=int(report.get("resilience_score", 0)),
                recovery_score=int(report.get("recovery_score", 0)),
                latency_score=int(report.get("latency_score", 0)),
                error_score=int(report.get("error_score", 0)),
                probe_integrity_score=int(report.get("probe_integrity_score", 0)),
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
                RecoveryWindowHistory.recovery_window_seconds,
                RecoveryWindowHistory.readiness_false_positive,
                LatencyErrorSummary.latency_p95_ms,
                LatencyErrorSummary.error_rate,
                LatencyErrorSummary.latency_p95_drift_pct,
                LatencyErrorSummary.error_rate_delta,
            )
            .join(ScoreHistory, ScoreHistory.run_id == ScenarioRun.run_id)
            .join(RecoveryWindowHistory, RecoveryWindowHistory.run_id == ScenarioRun.run_id)
            .join(LatencyErrorSummary, LatencyErrorSummary.run_id == ScenarioRun.run_id)
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
                func.sum(func.cast(RecoveryWindowHistory.readiness_false_positive, Integer)).label("readiness_false_positive_count"),
            )
            .join(ScoreHistory, ScoreHistory.run_id == ScenarioRun.run_id)
            .join(RecoveryWindowHistory, RecoveryWindowHistory.run_id == ScenarioRun.run_id)
            .join(LatencyErrorSummary, LatencyErrorSummary.run_id == ScenarioRun.run_id)
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
PY

cat > app/statistics_engine.py <<'PY'
from sqlalchemy import select
from scipy.stats import chi2_contingency, ttest_ind
from app.db import get_db_session
from app.models import LatencyErrorSummary, RecoveryWindowHistory, ScenarioRun

def _safe_ttest(a: list[float], b: list[float]) -> dict:
    if len(a) < 2 or len(b) < 2:
        return {"supported": False, "note": "Need at least 2 runs in each group for a t-test."}
    stat, pvalue = ttest_ind(a, b, equal_var=False)
    return {"supported": True, "t_statistic": round(float(stat), 4), "p_value": round(float(pvalue), 6)}

def _safe_chi2(table: list[list[int]]) -> dict:
    if sum(sum(row) for row in table) == 0:
        return {"supported": False, "note": "No observations available for chi-squared comparison."}
    chi2, pvalue, _, expected = chi2_contingency(table)
    return {
        "supported": True,
        "chi2_statistic": round(float(chi2), 4),
        "p_value": round(float(pvalue), 6),
        "expected": [[round(float(cell), 3) for cell in row] for row in expected],
    }

def compare_baseline_vs_degraded(scenario: str, run_group: str | None = None) -> dict:
    with get_db_session() as session:
        stmt = (
            select(
                ScenarioRun.run_kind,
                ScenarioRun.status,
                RecoveryWindowHistory.readiness_false_positive,
                RecoveryWindowHistory.recovery_window_seconds,
                LatencyErrorSummary.latency_p95_ms,
            )
            .join(RecoveryWindowHistory, RecoveryWindowHistory.run_id == ScenarioRun.run_id)
            .join(LatencyErrorSummary, LatencyErrorSummary.run_id == ScenarioRun.run_id)
            .where(ScenarioRun.scenario == scenario)
            .where(ScenarioRun.run_kind.in_(["baseline", "degraded"]))
        )
        if run_group:
            stmt = stmt.where(ScenarioRun.run_group == run_group)

        rows = [dict(row._mapping) for row in session.execute(stmt).all()]

    baseline = [r for r in rows if r["run_kind"] == "baseline"]
    degraded = [r for r in rows if r["run_kind"] == "degraded"]

    baseline_latency = [float(r["latency_p95_ms"]) for r in baseline]
    degraded_latency = [float(r["latency_p95_ms"]) for r in degraded]
    baseline_recovery = [float(r["recovery_window_seconds"]) for r in baseline]
    degraded_recovery = [float(r["recovery_window_seconds"]) for r in degraded]

    pass_fail_table = [
        [sum(1 for r in baseline if r["status"] == "pass"), sum(1 for r in baseline if r["status"] != "pass")],
        [sum(1 for r in degraded if r["status"] == "pass"), sum(1 for r in degraded if r["status"] != "pass")],
    ]
    readiness_table = [
        [sum(1 for r in baseline if not r["readiness_false_positive"]), sum(1 for r in baseline if r["readiness_false_positive"])],
        [sum(1 for r in degraded if not r["readiness_false_positive"]), sum(1 for r in degraded if r["readiness_false_positive"])],
    ]

    return {
        "scenario": scenario,
        "run_group": run_group,
        "baseline_count": len(baseline),
        "degraded_count": len(degraded),
        "latency_p95_ttest": _safe_ttest(baseline_latency, degraded_latency),
        "recovery_window_ttest": _safe_ttest(baseline_recovery, degraded_recovery),
        "pass_fail_chi_squared": _safe_chi2(pass_fail_table),
        "readiness_integrity_chi_squared": _safe_chi2(readiness_table),
        "contingency_tables": {
            "pass_fail": pass_fail_table,
            "readiness_integrity": readiness_table,
        },
    }
PY

cat > app/dashboard_export.py <<'PY'
import csv
from pathlib import Path
from sqlalchemy import select
from app.db import get_db_session
from app.models import LatencyErrorSummary, RecoveryWindowHistory, ScenarioRun, ScoreHistory

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
                RecoveryWindowHistory.recovery_window_seconds,
                RecoveryWindowHistory.restart_count,
                RecoveryWindowHistory.readiness_false_positive,
                LatencyErrorSummary.latency_p95_ms,
                LatencyErrorSummary.latency_p95_drift_pct,
                LatencyErrorSummary.error_rate,
                LatencyErrorSummary.error_rate_delta,
            )
            .join(ScoreHistory, ScoreHistory.run_id == ScenarioRun.run_id)
            .join(RecoveryWindowHistory, RecoveryWindowHistory.run_id == ScenarioRun.run_id)
            .join(LatencyErrorSummary, LatencyErrorSummary.run_id == ScenarioRun.run_id)
            .order_by(ScenarioRun.created_at.asc())
        ).all()

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "run_id", "scenario", "run_group", "run_kind", "status", "validity_status",
            "confidence_score", "created_at", "recommendation", "resilience_score",
            "recovery_window_seconds", "restart_count", "readiness_false_positive",
            "latency_p95_ms", "latency_p95_drift_pct", "error_rate", "error_rate_delta"
        ])
        for row in rows:
            writer.writerow(list(row))
    return str(output)
PY

cat > dashboards/powerbi/README.md <<'MD'
# KubePulse Power BI Dashboard

Use `exports/dashboard_dataset.csv` as the source.

Recommended visuals:
1. resilience score by scenario over time
2. recovery-window trend by scenario
3. latency drift by disruption type
4. error-rate delta by scenario
5. readiness false-positive counts
6. recommendation distribution
7. run validity and confidence table
MD

chmod +x scripts/apply_analytics_layer.sh
echo "Analytics layer files written."
