import subprocess
from datetime import datetime, timezone


def _run_kubectl_command(command_parts: list[str]) -> dict:
    start_time = datetime.now(timezone.utc)

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

    end_time = datetime.now(timezone.utc)

    return {
        "started_at": start_time.isoformat(),
        "ended_at": end_time.isoformat(),
        "success": success,
        "stdout": completed.stdout if hasattr(completed, "stdout") else "",
        "stderr": completed.stderr if hasattr(completed, "stderr") else "",
        "error": error,
    }


def inject_cpu_stress(pod_name: str, namespace: str = "default") -> dict:
    if not pod_name:
        raise ValueError("Invalid pod name provided.")

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


def inject_memory_stress(pod_name: str, namespace: str = "default") -> dict:
    if not pod_name:
        raise ValueError("Invalid pod name provided.")

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
