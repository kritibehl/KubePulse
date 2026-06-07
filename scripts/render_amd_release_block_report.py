from pathlib import Path
import matplotlib.pyplot as plt

lines = [
    "AMD AI Serving Release Gate",
    "",
    "device = amd_accelerator_node",
    "gpu_memory_pressure = 88%",
    "token_latency = 1422 ms",
    "throughput_delta = -18%",
    "error_rate = 5%",
    "release_decision = block",
    "rollback_required = true",
    "",
    "safe scope: workload-level validation, not CUDA/kernel work"
]

out = Path("amd_ai_serving/screenshots/amd_release_decision_block.png")
out.parent.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(9, 5))
ax.axis("off")

for i, line in enumerate(lines):
    ax.text(0.03, 0.93 - i * 0.075, line, fontsize=13, family="monospace")

plt.tight_layout()
plt.savefig(out)
plt.close()

print(f"wrote {out}")
