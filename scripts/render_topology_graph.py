import json
from pathlib import Path
import matplotlib.pyplot as plt

data = json.loads(Path("topology/dependency_graph.json").read_text())

positions = {
    "gateway": (0, 2),
    "checkout": (2, 2),
    "inventory": (4, 3),
    "payments": (4, 1),
    "recommendations": (2, 0),
}

out = Path("docs/images")
out.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(8, 4.8))

for src, dst in data["edges"]:
    x1, y1 = positions[src]
    x2, y2 = positions[dst]
    plt.plot([x1, x2], [y1, y2])
    plt.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->"))

for svc, (x, y) in positions.items():
    label = svc
    if svc == data["failure_root"]:
        label += "\nROOT FAILURE"
    elif svc in data["impacted_services"]:
        label += "\nIMPACTED"
    plt.scatter([x], [y], s=800)
    plt.text(x, y, label, ha="center", va="center", fontsize=8)

plt.title("KubePulse Failure Propagation Topology")
plt.axis("off")
plt.tight_layout()
plt.savefig(out / "failure_propagation_topology.png")
plt.close()

print("wrote docs/images/failure_propagation_topology.png")
