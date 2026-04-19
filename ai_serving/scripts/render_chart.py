import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt

base = json.load(open(sys.argv[1]))
cand = json.load(open(sys.argv[2]))
out = sys.argv[3]

labels = ["baseline", "candidate"]
values = [base.get("latency_p95_ms", 0.0), cand.get("latency_p95_ms", 0.0)]

Path(out).parent.mkdir(parents=True, exist_ok=True)
plt.figure(figsize=(7, 4.2))
plt.bar(labels, values)
plt.ylabel("p95 latency (ms)")
plt.title("AI Serving Baseline vs Candidate")
plt.tight_layout()
plt.savefig(out)
plt.close()
print(out)
