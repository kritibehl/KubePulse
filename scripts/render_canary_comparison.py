import json
from pathlib import Path
import matplotlib.pyplot as plt

data = json.loads(Path("canary/baseline_vs_candidate.json").read_text())

out = Path("docs/images")
out.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(7, 4))
plt.bar(
    ["baseline p95", "candidate p95"],
    [
        data["baseline"]["p95_latency_ms"],
        data["candidate"]["p95_latency_ms"],
    ],
)
plt.ylabel("p95 latency (ms)")
plt.title("Canary Baseline vs Candidate")
plt.tight_layout()
plt.savefig(out / "canary_baseline_vs_candidate.png")
plt.close()

report = f"""# Canary Release Comparison

Release ID: {data["release_id"]}

| Signal | Baseline | Candidate |
|---|---:|---:|
| p95 latency | {data["baseline"]["p95_latency_ms"]} ms | {data["candidate"]["p95_latency_ms"]} ms |
| error rate | {data["baseline"]["error_rate"]} | {data["candidate"]["error_rate"]} |
| safe to operate | {data["baseline"]["safe_to_operate"]} | {data["candidate"]["safe_to_operate"]} |

## Decision

Rollout decision: `{data["rollout_decision"]}`

Rollback recommended: `{data["rollback_recommended"]}`

p95 regression: {data["delta"]["p95_latency_regression_percent"]}%
"""

Path("canary/canary_comparison_report.md").write_text(report)
print("wrote docs/images/canary_baseline_vs_candidate.png")
print("wrote canary/canary_comparison_report.md")
