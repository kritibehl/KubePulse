import subprocess

def inject_cpu_stress(pod_name, namespace="default"):
    """
    Inject CPU stress on a given pod.
    """
    if not pod_name:
        raise ValueError("Invalid pod name provided.")
    
    print(f"Injecting CPU stress on pod {pod_name} in namespace {namespace}")
    stressors = ["stress", "--cpu", "1", "--timeout", "60s"]
    command = f"kubectl exec -n {namespace} {pod_name} -- {stressors}"
    
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"CPU stress injected on pod {pod_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error injecting CPU stress on pod {pod_name}: {e}")
        raise


def inject_memory_stress(pod_name, namespace="default"):
    """
    Inject memory stress on a given pod.
    """
    if not pod_name:
        raise ValueError("Invalid pod name provided.")
    
    print(f"Injecting memory stress on pod {pod_name} in namespace {namespace}")
    stressors = ["stress", "--vm", "1", "--vm-bytes", "50M", "--timeout", "60s"]
    command = f"kubectl exec -n {namespace} {pod_name} -- {stressors}"
    
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Memory stress injected on pod {pod_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error injecting memory stress on pod {pod_name}: {e}")
        raise
