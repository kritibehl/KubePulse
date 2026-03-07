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

    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    report_path: Optional[str] = None
