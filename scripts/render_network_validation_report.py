from pathlib import Path
import matplotlib.pyplot as plt

out = Path("netroute_lab/screenshots/network_validation_report.png")

findings = [
    ("latency violation", 92),
    ("packet loss", 4.8),
    ("capacity headroom", 8),
]

labels = [x[0] for x in findings]
values = [x[1] for x in findings]

plt.figure(figsize=(8, 4))
plt.bar(labels, values)
plt.title("NetRouteLab Validation Findings")
plt.ylabel("observed value")
plt.tight_layout()
plt.savefig(out)
plt.close()

print(f"wrote {out}")
