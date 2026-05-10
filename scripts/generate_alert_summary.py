import json
from pathlib import Path

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

sample = {
    "service": "kubepulse",
    "alert_triggered": True,
    "threshold_violated": "p95_latency_regression",
    "probable_cause": "long_prompt_burst_resource_saturation",
    "recommended_remediation": "rollback_candidate_release",
    "runbook_link": "ops/incident_response_runbook.md",
    "status_lifecycle": ["detected", "acknowledged", "remediated"],
    "security_compliance": {
        "runbook_attached": True,
        "acknowledgement_required": True,
        "audit_status": "recorded"
    }
}

out_json = REPORT_DIR / "alert_summary.json"
out_md = REPORT_DIR / "alert_summary.md"

out_json.write_text(json.dumps(sample, indent=2))

out_md.write_text(f"""# KubePulse Alert Summary

Alert triggered: {sample["alert_triggered"]}

Threshold violated: {sample["threshold_violated"]}

Probable cause: {sample["probable_cause"]}

Recommended remediation: {sample["recommended_remediation"]}

Runbook: `{sample["runbook_link"]}`

Status lifecycle: detected -> acknowledged -> remediated

Security/compliance:
- runbook attached: true
- acknowledgement required: true
- audit status: recorded
""")

print(f"wrote {out_json}")
print(f"wrote {out_md}")
