import json
from pathlib import Path
from network_operations_pack.ops_pack import as_dicts

reports = Path("reports")
reports.mkdir(exist_ok=True)

incidents = as_dicts()

json_path = reports / "network_operations_pack.json"
md_path = reports / "network_operations_pack.md"

json_path.write_text(json.dumps({"network_operations_incidents": incidents}, indent=2))

lines = [
    "# Network Operations Pack",
    "",
    "This pack maps KubePulse diagnostics to production network-operations workflows.",
    "",
    "| Scenario | Severity | Symptom | Probable Root Cause | Operate Decision | Release Decision |",
    "|---|---|---|---|---|---|",
]

for incident in incidents:
    lines.append(
        f"| {incident['scenario']} | {incident['incident_severity']} | "
        f"{incident['detected_symptom']} | {incident['probable_root_cause']} | "
        f"{incident['operate_decision']} | {incident['release_decision']} |"
    )

lines += [
    "",
    "## Diagnostic Command Coverage",
    "",
]

for incident in incidents:
    lines.append(f"### {incident['scenario']}")
    lines.append("")
    lines.append("Commands used:")
    lines.extend([f"- `{cmd}`" for cmd in incident["commands_used_for_diagnosis"]])
    lines.append("")
    lines.append("Pre-change verification:")
    lines.extend([f"- {step}" for step in incident["pre_change_verification"]])
    lines.append("")
    lines.append("Post-change verification:")
    lines.extend([f"- {step}" for step in incident["post_change_verification"]])
    lines.append("")
    lines.append(f"Recommended escalation: {incident['recommended_escalation']}")
    lines.append("")

md_path.write_text("\n".join(lines))
print(f"Wrote {json_path}")
print(f"Wrote {md_path}")
