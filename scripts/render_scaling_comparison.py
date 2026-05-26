import json
from pathlib import Path
import matplotlib.pyplot as plt

data = json.loads(Path("scaling/horizontal_scaling_comparison.json").read_text())
runs = data["runs"]

replicas = [r["replicas"] for r in runs]
p95 = [r["p95_latency_ms"] for r in runs]
queue = [r["queue_depth"] for r in runs]

out = Path("reports/scaling")
out.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(8, 4))
plt.plot(replicas, p95, marker="o")
plt.title("Horizontal Scaling: p95 Latency Recovery")
plt.xlabel("replicas")
plt.ylabel("p95 latency ms")
plt.tight_layout()
plt.savefig(out / "horizontal_scaling_latency.png")
plt.close()

plt.figure(figsize=(8, 4))
plt.plot(replicas, queue, marker="o")
plt.title("Horizontal Scaling: Queue Depth Recovery")
plt.xlabel("replicas")
plt.ylabel("queue depth")
plt.tight_layout()
plt.savefig(out / "horizontal_scaling_queue.png")
plt.close()

report = ["# Horizontal Scaling Comparison", ""]
report.append("| Replicas | Queue Depth | p95 ms | p99 ms | Error Rate | Status |")
report.append("|---:|---:|---:|---:|---:|---|")
for r in runs:
    report.append(
        f"| {r['replicas']} | {r['queue_depth']} | {r['p95_latency_ms']} | {r['p99_latency_ms']} | {r['error_rate']} | {r['status']} |"
    )

report.extend([
    "",
    f"Autoscaling recovery time: `{data['autoscaling_recovery_seconds']}s`",
    "",
    f"Release decision: `{data['release_decision']}`",
    "",
    f"Reason: {data['reason']}"
])

(out / "horizontal_scaling_comparison.md").write_text("\n".join(report))

print("wrote reports/scaling/horizontal_scaling_latency.png")
print("wrote reports/scaling/horizontal_scaling_queue.png")
print("wrote reports/scaling/horizontal_scaling_comparison.md")
