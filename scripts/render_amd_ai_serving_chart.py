import json
from pathlib import Path
import matplotlib.pyplot as plt

data = json.loads(Path("amd_ai_serving/amd_serving_metrics.json").read_text())
points = data["measurements"]

x = [p["gpu_memory_pressure_percent"] for p in points]
y = [p["token_latency_ms"] for p in points]

out = Path("amd_ai_serving/screenshots/token_latency_vs_memory_pressure.png")
out.parent.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(8, 4.5))
plt.plot(x, y, marker="o")
plt.title("Token Latency vs GPU Memory Pressure")
plt.xlabel("GPU memory pressure (%)")
plt.ylabel("Token latency (ms)")
plt.tight_layout()
plt.savefig(out)
plt.close()

print(f"wrote {out}")
