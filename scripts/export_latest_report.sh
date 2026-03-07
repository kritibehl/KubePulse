#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from app.report_store import list_reports
from app.report_exporter import export_report_markdown

reports = list_reports()
if not reports:
    raise SystemExit("No reports found")

latest = reports[-1]
output = export_report_markdown(latest)
print(output)
PY
