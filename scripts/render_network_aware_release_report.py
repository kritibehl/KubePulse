import json
from pathlib import Path
import matplotlib.pyplot as plt

out_img = Path("docs/images")
out_report = Path("docs/reports")
out_img.mkdir(parents=True, exist_ok=True)
out_report.mkdir(parents=True, exist_ok=True)

decision = json.loads(Path("netroute_lab/release_decisions/network_aware_release_decision.json").read_text())

# Architecture diagram
steps = [
    "DNS/TCP/TLS\nprobes",
    "NetRouteLab\nrisk scoring",
    "SLO + canary\nchecks",
    "Rollback\nengine",
    "Release\nBLOCK"
]

plt.figure(figsize=(11, 3.5))
for i, step in enumerate(steps):
    plt.scatter(i, 0, s=2200)
    plt.text(i, 0, step, ha="center", va="center", fontsize=9)
    if i < len(steps) - 1:
        plt.annotate("", xy=(i + 0.75, 0), xytext=(i + 0.25, 0), arrowprops=dict(arrowstyle="->"))
plt.title("KubePulse + NetRouteLab Network-Aware Release Decision Flow")
plt.axis("off")
plt.tight_layout()
plt.savefig(out_img / "network_aware_release_architecture.png")
plt.close()

# Decision report chart
labels = ["packet loss %", "latency ms", "capacity headroom %", "risk score"]
values = [
    decision["packet_loss_pct"],
    decision["latency_ms"],
    decision["capacity_headroom_pct"],
    decision["dependency_risk_score"],
]

plt.figure(figsize=(8, 4))
plt.bar(labels, values)
plt.title("Network-Aware Release Block Signals")
plt.ylabel("observed value")
plt.tight_layout()
plt.savefig(out_img / "network_aware_release_block_report.png")
plt.close()

html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>KubePulse Network-Aware Release Decision</title>
</head>
<body>
  <h1>KubePulse + NetRouteLab Release Decision Report</h1>
  <h2>Decision</h2>
  <ul>
    <li><b>Safe to operate:</b> {decision["safe_to_operate"]}</li>
    <li><b>Release decision:</b> {decision["release_decision"]}</li>
    <li><b>Dependency risk score:</b> {decision["dependency_risk_score"]}</li>
    <li><b>Degraded path:</b> {decision["degraded_path"]}</li>
  </ul>

  <h2>Blocked Reasons</h2>
  <ul>
    {''.join(f'<li>{reason}</li>' for reason in decision["blocked_reason"])}
  </ul>

  <h2>Recommended Remediation</h2>
  <ul>
    {''.join(f'<li>{action}</li>' for action in decision["recommended_remediation"])}
  </ul>

  <h2>Visuals</h2>
  <img src="../images/network_aware_release_architecture.png" width="900">
  <br>
  <img src="../images/network_aware_release_block_report.png" width="700">
</body>
</html>
"""

(out_report / "network_aware_release_decision.html").write_text(html)

print("wrote docs/images/network_aware_release_architecture.png")
print("wrote docs/images/network_aware_release_block_report.png")
print("wrote docs/reports/network_aware_release_decision.html")
