import json
from pathlib import Path
import matplotlib.pyplot as plt

data = json.loads(Path("slo/availability_budget.json").read_text())

labels = ["availability budget used", "error budget burned", "recovery window"]
values = [
    100 - data["budget_status"]["availability_budget_remaining_percent"],
    data["budget_status"]["error_budget_burned_percent"],
    data["observed"]["recovery_time_seconds"],
]

out = Path("slo/slo_dashboard.png")

plt.figure(figsize=(8, 4))
plt.bar(labels, values)
plt.title("KubePulse SLO / Error-Budget Dashboard")
plt.ylabel("percent / seconds")
plt.tight_layout()
plt.savefig(out)
plt.close()

print(f"wrote {out}")
