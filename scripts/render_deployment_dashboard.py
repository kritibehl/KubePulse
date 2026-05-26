from pathlib import Path
import matplotlib.pyplot as plt

out = Path("docs/screenshots/deployment_safety_dashboard.png")
out.parent.mkdir(parents=True, exist_ok=True)

labels = ["Wave 1\nblocked", "Wave 2\nfrozen", "Wave 3\nfrozen", "Rollback\ntriggered", "Recovery\nmonitoring"]
values = [1, 0.6, 0.6, 1, 0.7]

plt.figure(figsize=(10, 4.8))
plt.bar(labels, values)
plt.title("KubePulse Deployment Safety Dashboard")
plt.ylabel("state intensity")
plt.tight_layout()
plt.savefig(out)
plt.close()

print(f"wrote {out}")
