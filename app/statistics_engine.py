from sqlalchemy import select
from scipy.stats import chi2_contingency, ttest_ind
from app.db import get_db_session
from app.models import LatencyErrorSummary, RecoveryWindowHistory, ScenarioRun

def _safe_ttest(a: list[float], b: list[float]) -> dict:
    if len(a) < 2 or len(b) < 2:
        return {"supported": False, "note": "Need at least 2 runs in each group for a t-test."}
    if len(set(a)) == 1 and len(set(b)) == 1 and a[0] == b[0]:
        return {"supported": False, "note": "No variance between groups; t-test is not meaningful."}
    stat, pvalue = ttest_ind(a, b, equal_var=False)
    return {"supported": True, "t_statistic": round(float(stat), 4), "p_value": round(float(pvalue), 6)}

def _safe_chi2(table: list[list[int]]) -> dict:
    total = sum(sum(row) for row in table)
    if total == 0:
        return {"supported": False, "note": "No observations available for chi-squared comparison."}

    row_sums = [sum(row) for row in table]
    col_sums = [sum(col) for col in zip(*table)]

    if 0 in row_sums or 0 in col_sums:
        return {"supported": False, "note": "Chi-squared is not meaningful for a degenerate contingency table."}

    try:
        chi2, pvalue, _, expected = chi2_contingency(table)
        return {
            "supported": True,
            "chi2_statistic": round(float(chi2), 4),
            "p_value": round(float(pvalue), 6),
            "expected": [[round(float(cell), 3) for cell in row] for row in expected],
        }
    except Exception as exc:
        return {"supported": False, "note": f"Chi-squared could not be computed: {exc}"}

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
