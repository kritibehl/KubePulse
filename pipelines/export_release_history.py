import json
from pathlib import Path

BOARD = Path("reports/release_history/release_history_board.json")
OUT = Path("reports/release_history/release_history_summary.md")

with BOARD.open() as f:
    data = json.load(f)

rows = data["release_history_board"]
summary = data["summary"]

lines = [
    "# Release History Summary",
    "",
    "## Totals",
    "",
    f"- Approved releases: {summary['approved_releases']}",
    f"- Blocked releases: {summary['blocked_releases']}",
    f"- Rollback required: {summary['rollback_required']}",
    "",
    "## Release Board",
    "",
    "| Release | Service | Decision | Rollback Required | Reason | p95 Delta | p99 Delta | Readiness |",
    "|---|---|---|---:|---|---:|---:|---|",
]

for r in rows:
    lines.append(
        f"| {r['release_id']} | {r['service']} | {r['decision']} | {r['rollback_required']} | "
        f"{r['reason']} | {r['p95_latency_delta_pct']}% | {r['p99_latency_delta_pct']}% | {r['release_readiness']} |"
    )

OUT.write_text("\n".join(lines) + "\n")
print(f"Wrote {OUT}")
