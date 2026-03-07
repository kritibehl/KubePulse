import subprocess
import json


def get_pod_restarts(pod, namespace="default"):
    cmd = [
        "kubectl",
        "get",
        "pod",
        pod,
        "-n",
        namespace,
        "-o",
        "json"
    ]

    output = subprocess.check_output(cmd).decode()
    data = json.loads(output)

    restarts = 0
    for c in data["status"]["containerStatuses"]:
        restarts += c["restartCount"]

    return restarts


def get_pod_ready(pod, namespace="default"):
    cmd = [
        "kubectl",
        "get",
        "pod",
        pod,
        "-n",
        namespace,
        "-o",
        "json"
    ]

    output = subprocess.check_output(cmd).decode()
    data = json.loads(output)

    for cond in data["status"]["conditions"]:
        if cond["type"] == "Ready":
            return cond["status"] == "True"

    return False
