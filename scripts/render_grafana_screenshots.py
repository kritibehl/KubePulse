from pathlib import Path
import matplotlib.pyplot as plt

out = Path("grafana/screenshots")
out.mkdir(parents=True, exist_ok=True)

charts = [
    ("p95_spike.png", "p95 Latency Spike", ["baseline", "burst"], [200.76, 1422.07], "p95 latency (ms)"),
    ("release_block.png", "Release Decision", ["continue", "block"], [0, 1], "blocked = 1"),
    ("alert_firing.png", "Alert Firing", ["normal", "threshold violated"], [0, 1], "alert = 1"),
    ("recovery_window.png", "Recovery Window", ["target", "observed"], [10, 12], "seconds"),
    ("degraded_path_requests.png", "Degraded Path Requests", ["baseline", "degraded"], [0, 37], "requests"),
]

for filename, title, labels, values, ylabel in charts:
    plt.figure(figsize=(7, 4))
    plt.bar(labels, values)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(out / filename)
    plt.close()

print("wrote grafana/screenshots/*.png")
