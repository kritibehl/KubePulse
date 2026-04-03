from typing import Optional
from pydantic import BaseModel

class ScenarioRequest(BaseModel):
    pod_name: str
    namespace: str = "default"
    dry_run: bool = False

class HistoricalScenarioRequest(ScenarioRequest):
    run_group: Optional[str] = None
    run_kind: Optional[str] = None

class NetworkScenarioRequest(BaseModel):
    namespace: str = "default"
    source_service: str
    target_service: str
    dry_run: bool = True
    run_group: Optional[str] = None
    run_kind: Optional[str] = None
    severity: str = "medium"
    duration_seconds: int = 30

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
    network_health_score: int = 0
    dns_score: int = 0
    tcp_score: int = 0
    http_score: int = 0
    cross_zone_score: int = 0
    path_recovery_score: int = 0
    readiness_integrity_score: int = 0
    availability_alignment_score: int = 0
    dns_success_rate: float = 1.0
    tcp_connect_latency_ms: float = 0.0
    http_success_rate: float = 1.0
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
    recommended_action: Optional[str] = None
    confidence: float = 0.0
    suggested_rollback: Optional[str] = None
    suggested_config_change: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    report_path: Optional[str] = None
    readiness_before: str = "ready"
    readiness_after: str = "ready"
    readiness_false_positive: bool = False
    pass_fail_reason: str = "Scenario satisfied configured thresholds."
    recommendation: str = "No action required."
    run_id: Optional[str] = None
    run_group: Optional[str] = None
    run_kind: Optional[str] = None
    validity_status: str = "valid"
    confidence_score: float = 1.0
    data_sufficiency_notes: str = "Sufficient data captured for reporting."
    missing_fields: list[str] = []
    fallback_success_rate_pct: float = 0.0
    degraded_serving_mode: bool = False
    full_outage: bool = False
    user_visible_quality: str = "healthy"
    ai_dependency: Optional[str] = None
    ai_failure_mode: Optional[str] = None
    baseline_path: Optional[list[str]] = None
    baseline_path_cost: Optional[float] = None
    final_path: Optional[list[str]] = None
    final_path_cost: Optional[float] = None
    path_change_timeline: Optional[list[dict]] = None
    broken_hop: Optional[str] = None
    reroute_detail: Optional[dict] = None
    partial_recovery: bool = False
    convergence_seconds: float = 0.0
    path_changes_total: int = 0
    unreachable_windows_total: int = 0
    unreachable_window_seconds: float = 0.0
    degraded_path_requests_total: int = 0
    path_recovery_status: str = "stable"
    path_extra_latency_ms: float = 0.0
    probes_say_healthy: bool = False
    safe_to_operate: bool = False
    what_probes_missed: list[str] = []
    recommendation_action: Optional[str] = None
    decision_artifact: Optional[dict] = None
    degraded_hop: Optional[str] = None
    path_shift_summary: Optional[str] = None
    path_trace_correlation: Optional[dict] = None
    baseline_path: Optional[list[str]] = None
    baseline_path_cost: Optional[float] = None
    final_path: Optional[list[str]] = None
    final_path_cost: Optional[float] = None
    path_change_timeline: Optional[list[dict]] = None
    broken_hop: Optional[str] = None
    reroute_detail: Optional[dict] = None
    partial_recovery: bool = False
    convergence_seconds: float = 0.0
    path_changes_total: int = 0
    unreachable_windows_total: int = 0
    degraded_path_requests_total: int = 0
    path_extra_latency_ms: float = 0.0
