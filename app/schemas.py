from typing import List, Optional
from pydantic import BaseModel


class ScenarioRequest(BaseModel):
    pod_name: str = "demo-pod"
    namespace: str = "default"
    dry_run: bool = False


class HistoricalScenarioRequest(BaseModel):
    pod_name: str = "demo-pod"
    namespace: str = "default"
    dry_run: bool = True
    run_group: Optional[str] = None
    run_kind: Optional[str] = None


class NetworkScenarioRequest(BaseModel):
    namespace: str = "default"
    source_service: str = "frontend"
    target_service: str = "backend"
    dry_run: bool = True
    run_group: Optional[str] = None
    run_kind: Optional[str] = None


class ResilienceReport(BaseModel):
    scenario: str
    pod_name: str
    namespace: str
    started_at: str
    ended_at: str
    success: bool
    recovery_window_seconds: float
    restart_count: int
    probe_mismatch: bool
    status: str

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

    network_health_score: int = 0
    dns_score: int = 0
    tcp_score: int = 0
    http_score: int = 0
    cross_zone_score: int = 0
    path_recovery_score: int = 0
    readiness_integrity_score: int = 0
    availability_alignment_score: int = 0

    dns_success_rate: float = 0.0
    tcp_connect_latency_ms: float = 0.0
    http_success_rate: float = 0.0
    cross_zone_degradation_pct: float = 0.0
    path_recovery_time_seconds: float = 0.0
    network_availability_gap_pct: float = 0.0
    connection_failure_rate: float = 0.0
    packet_loss_pct: float = 0.0
    latency_injection_ms: float = 0.0
    tcp_reset_rate: float = 0.0
    mtu_mismatch_detected: bool = False

    source_service: Optional[str] = None
    target_service: Optional[str] = None
    probable_source_of_degradation: Optional[str] = None
    release_decision: Optional[str] = None
    release_decision: Optional[str] = None
    reason: Optional[str] = None
    confidence: float = 0.0
    suggested_rollback: Optional[str] = None
    suggested_config_change: Optional[str] = None

    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None
    report_path: Optional[str] = None

    readiness_before: Optional[str] = None
    readiness_after: Optional[str] = None
    readiness_false_positive: bool = False
    pass_fail_reason: Optional[str] = None
    recommendation: Optional[str] = None

    run_id: Optional[str] = None
    run_group: Optional[str] = None
    run_kind: Optional[str] = None

    validity_status: Optional[str] = None
    confidence_score: float = 0.0
    data_sufficiency_notes: Optional[str] = None
    missing_fields: List[str] = []
    fallback_success_rate_pct: float = 0.0
    degraded_serving_mode: bool = False
    full_outage: bool = False
    user_visible_quality: Optional[str] = None
    ai_dependency: Optional[str] = None
    ai_failure_mode: Optional[str] = None

    baseline_path: Optional[List[str]] = None
    baseline_path_cost: Optional[float] = None
    final_path: Optional[List[str]] = None
    final_path_cost: Optional[float] = None
    path_change_timeline: Optional[List[dict]] = None
    broken_hop: Optional[str] = None
    reroute_detail: Optional[dict] = None
    partial_recovery: bool = False
    convergence_seconds: float = 0.0
    path_changes_total: int = 0
    unreachable_windows_total: int = 0
    unreachable_window_seconds: float = 0.0
    degraded_path_requests_total: int = 0
    path_recovery_status: Optional[str] = None
    path_extra_latency_ms: float = 0.0
    probes_say_healthy: bool = False
    safe_to_operate: bool = False
    what_probes_missed: List[str] = []
    decision_artifact: Optional[dict] = None
    degraded_hop: Optional[str] = None
    path_shift_summary: Optional[str] = None
    path_trace_correlation: Optional[dict] = None
