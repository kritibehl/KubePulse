from pathlib import Path
import matplotlib.pyplot as plt

replicas = [1,3,5]
p95 = [1422,640,238]
queue = [180,64,12]

out = Path("docs/screenshots")
out.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(8,4))
plt.plot(replicas, p95, marker="o")
plt.title("Autoscaling Recovery — p95 Latency")
plt.xlabel("Replicas")
plt.ylabel("p95 latency (ms)")
plt.tight_layout()
plt.savefig(out / "autoscaling_latency_recovery.png")
plt.close()

plt.figure(figsize=(8,4))
plt.plot(replicas, queue, marker="o")
plt.title("Autoscaling Recovery — Queue Depth")
plt.xlabel("Replicas")
plt.ylabel("Queue Depth")
plt.tight_layout()
plt.savefig(out / "autoscaling_queue_recovery.png")
plt.close()

print("wrote autoscaling screenshots")
