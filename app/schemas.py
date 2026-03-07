from typing import Optional
from pydantic import BaseModel


class ScenarioRequest(BaseModel):
    pod_name: str
    namespace: str = "default"
    dry_run: bool = False


class ResilienceReport(BaseModel):
    scenario: str
    pod_name: str
    namespace: str
    started_at: str
    ended_at: str
    success: bool

    recovery_window_seconds: float = 0.0
    restart_count: int = 0
    probe_mismatch: bool = False
    status: str = "pass"

    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    error_rate: float = 0.0

    baseline_latency_p50_ms: float = 0.0
    baseline_latency_p95_ms: float = 0.0
    baseline_latency_p99_ms: float = 0.0
    baseline_error_rate: float = 0.0

    observed_latency_p50_ms: float = 0.0
    observed_latency_p95_ms: float = 0.0
    observed_latency_p99_ms: float = 0.0
    observed_error_rate: float = 0.0

    latency_p50_drift_pct: float = 0.0
    latency_p95_drift_pct: float = 0.0
    latency_p99_drift_pct: float = 0.0
    error_rate_delta: float = 0.0

    resilience_score: int = 0
    recovery_score: int = 0
    latency_score: int = 0
    error_score: int = 0
    probe_integrity_score: int = 0

    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    report_path: Optional[str] = None

    readiness_before: str = "ready"
    readiness_after: str = "ready"
    readiness_false_positive: bool = False

    pass_fail_reason: str = "Scenario satisfied configured thresholds."
    recommendation: str = "No action required."
