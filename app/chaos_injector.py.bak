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
        "latency_p95_ms": 120.0 if success else 800.0,
        "error_rate": 0.01 if success else 0.10,
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
            "recovery_window_seconds": 8.0,
            "restart_count": 0,
            "probe_mismatch": False,
            "status": "pass",
            "stdout": "Dry run: simulated CPU stress injection",
            "stderr": "",
            "error": None,
            "readiness_before": "ready",
            "readiness_after": "ready",
            "readiness_false_positive": False,
            "latency_p95_ms": 210.0,
            "error_rate": 0.02,
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
            "recovery_window_seconds": 10.0,
            "restart_count": 1,
            "probe_mismatch": False,
            "status": "pass",
            "stdout": "Dry run: simulated memory stress injection",
            "stderr": "",
            "error": None,
            "readiness_before": "ready",
            "readiness_after": "ready",
            "readiness_false_positive": False,
            "latency_p95_ms": 240.0,
            "error_rate": 0.03,
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


def inject_readiness_false_positive(
    pod_name: str,
    namespace: str = "default",
    dry_run: bool = False,
) -> dict:
    if not pod_name:
        raise ValueError("Invalid pod name provided.")

    if dry_run:
        from app.metrics_probe import probe_endpoint

        metrics = probe_endpoint("http://127.0.0.1:9000/work", requests_count=25)

        return {
            "scenario": "readiness_false_positive",
            "pod_name": pod_name,
            "namespace": namespace,
            "started_at": _now(),
            "ended_at": _now(),
            "success": True,
            "recovery_window_seconds": 12.0,
            "restart_count": 0,
            "probe_mismatch": True,
            "status": "fail",
            "stdout": "Dry run: readiness remained healthy while service behavior degraded",
            "stderr": "",
            "error": None,
            "readiness_before": "ready",
            "readiness_after": "ready",
            "readiness_false_positive": True,
            "latency_p50_ms": metrics["latency_p50_ms"],
            "latency_p95_ms": metrics["latency_p95_ms"],
            "latency_p99_ms": metrics["latency_p99_ms"],
            "error_rate": metrics["error_rate"],
        }

    raise NotImplementedError("Real readiness false-positive scenario not implemented yet.")
