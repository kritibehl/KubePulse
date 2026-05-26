from pathlib import Path
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 7))
ax.axis("off")

boxes = [
    ("Deployment Waves", 0.08, 0.75),
    ("Rollback Gate", 0.32, 0.75),
    ("Release Decision Engine", 0.56, 0.75),
    ("CloudWatch / Prometheus", 0.80, 0.75),

    ("KubePulse Core", 0.32, 0.48),
    ("NetRouteLab", 0.56, 0.48),

    ("Grafana Dashboard", 0.20, 0.20),
    ("Deployment UI", 0.50, 0.20),
    ("Recovery Monitor", 0.80, 0.20),
]

for label, x, y in boxes:
    ax.text(
        x,
        y,
        label,
        ha="center",
        va="center",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5", edgecolor="black", facecolor="#dceeff")
    )

connections = [
    ((0.08,0.75),(0.32,0.75)),
    ((0.32,0.75),(0.56,0.75)),
    ((0.56,0.75),(0.80,0.75)),
    ((0.32,0.75),(0.32,0.48)),
    ((0.56,0.75),(0.56,0.48)),
    ((0.32,0.48),(0.20,0.20)),
    ((0.32,0.48),(0.50,0.20)),
    ((0.56,0.48),(0.80,0.20)),
]

for (x1,y1),(x2,y2) in connections:
    ax.annotate(
        "",
        xy=(x2,y2),
        xytext=(x1,y1),
        arrowprops=dict(arrowstyle="->", lw=2)
    )

out = Path("docs/architecture/kubepulse_architecture.png")
out.parent.mkdir(parents=True, exist_ok=True)

plt.tight_layout()
plt.savefig(out)
plt.close()

print(f"wrote {out}")
