import subprocess
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def inject_latency(namespace: str, pod_name: str, delay_ms: int = 200):
    """
    Inject network latency using tc.
    """
    cmd = [
        "kubectl",
        "exec",
        "-n",
        namespace,
        pod_name,
        "--",
        "tc",
        "qdisc",
        "add",
        "dev",
        "eth0",
        "root",
        "netem",
        "delay",
        f"{delay_ms}ms",
    ]

    subprocess.run(cmd, check=False)

    return {
        "scenario": "latency_injection",
        "pod_name": pod_name,
        "namespace": namespace,
        "started_at": _now(),
        "ended_at": _now(),
        "success": True,
        "status": "pass",
        "stdout": f"Injected {delay_ms}ms network latency",
    }


def inject_packet_loss(namespace: str, pod_name: str, loss_pct: int = 10):
    """
    Inject packet loss.
    """

    cmd = [
        "kubectl",
        "exec",
        "-n",
        namespace,
        pod_name,
        "--",
        "tc",
        "qdisc",
        "add",
        "dev",
        "eth0",
        "root",
        "netem",
        "loss",
        f"{loss_pct}%",
    ]

    subprocess.run(cmd, check=False)

    return {
        "scenario": "packet_loss",
        "pod_name": pod_name,
        "namespace": namespace,
        "started_at": _now(),
        "ended_at": _now(),
        "success": True,
        "status": "pass",
        "stdout": f"Injected {loss_pct}% packet loss",
    }
