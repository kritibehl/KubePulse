import time
from app.signal_collector import get_pod_restarts


def collect_baseline(pod, namespace="default", duration=10):

    start = time.time()

    restart_before = get_pod_restarts(pod, namespace)

    time.sleep(duration)

    restart_after = get_pod_restarts(pod, namespace)

    return {
        "baseline_duration": duration,
        "restart_delta": restart_after - restart_before
    }
