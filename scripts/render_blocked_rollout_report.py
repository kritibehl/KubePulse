from pathlib import Path
import matplotlib.pyplot as plt

lines = [
    "KubePulse Release Safety Report",
    "",
    "release_decision = block",
    "rollback_triggered = true",
    "dependency_risk_score = 91",
    "cloudwatch_alarm = ALARM",
    "canary_validation = fail",
    "deployment_wave = frozen",
    "recovery_state = monitoring",
]

fig, ax = plt.subplots(figsize=(9,5))
ax.axis("off")

for i, line in enumerate(lines):
    ax.text(
        0.03,
        0.92 - i*0.1,
        line,
        fontsize=14,
        family="monospace"
    )

out = Path("docs/screenshots/blocked_rollout_report.png")
plt.tight_layout()
plt.savefig(out)
plt.close()

print(f"wrote {out}")
