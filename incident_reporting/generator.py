from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _incident_id(
    deployment_revision: str,
    detected_at: str,
) -> str:
    material = f"{deployment_revision}:{detected_at}"

    digest = hashlib.sha256(
        material.encode("utf-8")
    ).hexdigest()[:10]

    timestamp = datetime.fromisoformat(detected_at)
    compact = timestamp.strftime("%Y%m%dT%H%M%SZ")

    return f"INC-{compact}-{digest}"


def build_incident_report(
    *,
    deployment_revision: str,
    gate_result: dict[str, Any],
    rollback_triggered: bool,
    final_status: str,
    source: str = "kubepulse_reliability_gate",
    error_budget_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    detected_at = _utc_now().isoformat()

    violations = gate_result.get(
        "violations",
        [],
    )

    primary = (
        violations[0]
        if violations
        else None
    )

    recovery = next(
        (
            item
            for item in gate_result.get(
                "evaluations",
                [],
            )
            if item["metric"]
            == "recovery_time_seconds"
        ),
        None,
    )

    burn_block = (
        error_budget_result is not None
        and error_budget_result.get(
            "release_action"
        ) == "BLOCK"
    )

    if primary:
        violation_type = "slo"
    elif burn_block:
        violation_type = "error_budget"
    else:
        violation_type = None

    incident = {
        "incident_id": _incident_id(
            deployment_revision,
            detected_at,
        ),
        "deployment_revision": deployment_revision,
        "detected_at": detected_at,
        "source": source,
        "release_decision": gate_result[
            "decision"
        ],
        "violation_type": violation_type,
        "violated_slo": (
            primary["metric"]
            if primary
            else None
        ),
        "observed_value": (
            primary["observed"]
            if primary
            else None
        ),
        "threshold": (
            primary["threshold"]
            if primary
            else None
        ),
        "rollback_triggered": rollback_triggered,
        "recovery_seconds": (
            recovery["observed"]
            if recovery
            else None
        ),
        "final_status": final_status,
        "violated_slos": [
            {
                "metric": item["metric"],
                "label": item["label"],
                "observed": item["observed"],
                "operator": item["operator"],
                "threshold": item["threshold"],
                "unit": item["unit"],
                "status": item["status"],
            }
            for item in violations
        ],
        "slo_evaluations": gate_result.get(
            "evaluations",
            [],
        ),
    }

    if error_budget_result is not None:
        cumulative = error_budget_result[
            "cumulative"
        ]

        incident["error_budget"] = {
            "availability_slo_percent": (
                error_budget_result[
                    "availability_slo_percent"
                ]
            ),
            "allowed_error_percent": (
                error_budget_result[
                    "allowed_error_percent"
                ]
            ),
            "observed_availability_percent": (
                cumulative[
                    "observed_availability_percent"
                ]
            ),
            "budget_consumed_percent": (
                cumulative[
                    "budget_consumed_percent"
                ]
            ),
            "budget_remaining_percent": (
                cumulative[
                    "budget_remaining_percent"
                ]
            ),
            "budget_exhausted": (
                cumulative[
                    "budget_exhausted"
                ]
            ),
        }

        incident["burn_rates"] = {
            window: values["burn_rate"]
            for window, values
            in error_budget_result[
                "windows"
            ].items()
        }

        incident["burn_status"] = (
            error_budget_result[
                "burn_status"
            ]
        )

        incident["burn_reason"] = (
            error_budget_result[
                "reason"
            ]
        )

    return incident


def write_incident_artifacts(
    incident: dict[str, Any],
    output_dir: str | Path,
) -> tuple[Path, Path]:
    output = Path(output_dir)

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    incident_id = incident[
        "incident_id"
    ]

    json_path = output / f"{incident_id}.json"
    md_path = output / f"{incident_id}.md"

    json_path.write_text(
        json.dumps(
            incident,
            indent=2,
        )
        + "\n"
    )

    violations = incident[
        "violated_slos"
    ]

    if violations:
        rows = "\n".join(
            (
                f"| {item['label']} "
                f"| {item['observed']} {item['unit']} "
                f"| {item['operator']} "
                f"{item['threshold']} {item['unit']} "
                f"| {item['status']} |"
            )
            for item in violations
        )
    else:
        rows = "| None | - | - | PASS |"

    burn_section = ""

    if "error_budget" in incident:
        budget = incident[
            "error_budget"
        ]

        burns = incident[
            "burn_rates"
        ]

        burn_rows = "\n".join(
            f"| {window} | {rate}x |"
            for window, rate
            in burns.items()
        )

        burn_section = f"""
## Error Budget

- **Availability SLO:** `{budget['availability_slo_percent']}%`
- **Observed availability:** `{budget['observed_availability_percent']}%`
- **Allowed error:** `{budget['allowed_error_percent']}%`
- **Budget consumed:** `{budget['budget_consumed_percent']}%`
- **Budget remaining:** `{budget['budget_remaining_percent']}%`
- **Budget exhausted:** `{str(budget['budget_exhausted']).lower()}`
- **Burn status:** `{incident['burn_status']}`

## Burn Rates

| Window | Burn rate |
| --- | ---: |
{burn_rows}
"""

    markdown = f"""# KubePulse Incident Report

## Incident

- **Incident ID:** `{incident['incident_id']}`
- **Deployment revision:** `{incident['deployment_revision']}`
- **Detected at:** `{incident['detected_at']}`
- **Release decision:** `{incident['release_decision']}`
- **Violation type:** `{incident['violation_type']}`
- **Rollback triggered:** `{str(incident['rollback_triggered']).lower()}`
- **Recovery time:** `{incident['recovery_seconds']}` seconds
- **Final status:** `{incident['final_status']}`

## SLO Violations

| SLO | Observed | Required | Status |
| --- | ---: | ---: | --- |
{rows}
{burn_section}
## Operational Sequence

SLI measurements
→ SLO evaluation
→ error-budget accounting
→ multi-window burn-rate classification
→ {incident['release_decision']}
→ rollback={str(incident['rollback_triggered']).lower()}
→ final_status={incident['final_status']}

## Evidence

This report is generated from structured reliability measurements.
KubePulse does not infer a root cause beyond supplied evidence.
"""

    md_path.write_text(markdown)

    return json_path, md_path
