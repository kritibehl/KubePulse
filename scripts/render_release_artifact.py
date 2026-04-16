#!/usr/bin/env python3
import json
import sys
import matplotlib.pyplot as plt

with open(sys.argv[1]) as f:
    report = json.load(f)

metrics = {
    "p50": report.get("latency_p50_ms", 0),
    "p95": report.get("latency_p95_ms", 0),
    "p99": report.get("latency_p99_ms", 0),
}
plt.figure(figsize=(6,4))
plt.bar(list(metrics.keys()), list(metrics.values()))
plt.title("KubePulse Latency Artifact")
plt.ylabel("ms")
plt.tight_layout()
plt.savefig("release_artifact_latency.png")
print("Saved release_artifact_latency.png")
