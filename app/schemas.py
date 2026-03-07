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
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    report_path: Optional[str] = None