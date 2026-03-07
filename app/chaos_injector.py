import subprocess
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_kubectl_command(command_parts: list[str]) -> dict:
    start_time = _now()

    try:
        completed = subprocess.run(
            command_parts,
            check=True,
            capture_output=True,
            text=True,
        )
        success = True
        error = None
    except subprocess.CalledProcessError as e:
        completed = e
        success = False
        error = str(e)

    end_time = _now()

    return {
        "started_at": start_time,
        "ended_at": end_time,
        "success": success,
        "recovery_window_seconds": 0.0,
        "restart_count": 0,
        "probe_mismatch": False,
        "status": "pass" if success else "fail",
        "stdout": completed.stdout if hasattr(completed, "stdout") else "",
        "stderr": completed.stderr if hasattr(completed, "stderr") else "",
        "error": error,
        "readiness_before": "ready",
        "readiness_after": "ready" if success else "not_ready",
        "readiness_false_positive": False,
    }


def inject_cpu_stress(
    pod_name: str,
    namespace: str = "default",
    dry_run: bool = False,
) -> dict:
    if not pod_name:
        raise ValueError("Invalid pod name provided.")

    if dry_run:
        return {
            "scenario": "cpu_stress",
            "pod_name": pod_name,
            "namespace": namespace,
            "started_at": _now(),
            "ended_at": _now(),
            "success": True,
            "recovery_window_seconds": 0.0,
            "restart_count": 0,
            "probe_mismatch": False,
            "status": "pass",
            "stdout": "Dry run: simulated CPU stress injection",
            "stderr": "",
            "error": None,
            "readiness_before": "ready",
            "readiness_after": "ready",
            "readiness_false_positive": False,
        }

    command = [
        "kubectl",
        "exec",
        "-n",
        namespace,
        pod_name,
        "--",
        "stress",
        "--cpu",
        "1",
        "--timeout",
        "60s",
    ]

    result = _run_kubectl_command(command)
    result.update(
        {
            "scenario": "cpu_stress",
            "pod_name": pod_name,
            "namespace": namespace,
        }
    )
    return result


def inject_memory_stress(
    pod_name: str,
    namespace: str = "default",
    dry_run: bool = False,
) -> dict:
    if not pod_name:
        raise ValueError("Invalid pod name provided.")

    if dry_run:
        return {
            "scenario": "memory_stress",
            "pod_name": pod_name,
            "namespace": namespace,
            "started_at": _now(),
            "ended_at": _now(),
            "success": True,
            "recovery_window_seconds": 0.0,
            "restart_count": 0,
            "probe_mismatch": False,
            "status": "pass",
            "stdout": "Dry run: simulated memory stress injection",
            "stderr": "",
            "error": None,
            "readiness_before": "ready",
            "readiness_after": "ready",
            "readiness_false_positive": False,
        }

    command = [
        "kubectl",
        "exec",
        "-n",
        namespace,
        pod_name,
        "--",
        "stress",
        "--vm",
        "1",
        "--vm-bytes",
        "50M",
        "--timeout",
        "60s",
    ]

    result = _run_kubectl_command(command)
    result.update(
        {
            "scenario": "memory_stress",
            "pod_name": pod_name,
            "namespace": namespace,
        }
    )
    return result
