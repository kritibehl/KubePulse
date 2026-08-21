#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from incident_reporting.generator import (
    build_incident_report,
    write_incident_artifacts,
)
from reliability.error_budget import (
    evaluate_error_budget,
)
from slo.evaluator import evaluate_slos


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate KubePulse SLOs, "
            "error budgets, and burn rates"
        )
    )

    parser.add_argument(
        "--slo-metrics",
        required=True,
    )

    parser.add_argument(
        "--reliability-metrics",
        required=True,
    )

    parser.add_argument(
        "--deployment-revision",
        required=True,
    )

    parser.add_argument(
        "--output",
        default=(
            "artifacts/reliability/"
            "release_evaluation.json"
        ),
    )

    parser.add_argument(
        "--incident-output-dir",
        default="artifacts/incidents",
    )

    parser.add_argument(
        "--rollback-triggered",
        action="store_true",
    )

    parser.add_argument(
        "--final-status",
        default="healthy",
    )

    args = parser.parse_args()

    slo_metrics = json.loads(
        Path(args.slo_metrics).read_text()
    )

    reliability_metrics = json.loads(
        Path(
            args.reliability_metrics
        ).read_text()
    )

    slo_result = evaluate_slos(
        slo_metrics
    )

    budget_result = (
        evaluate_error_budget(
            reliability_metrics
        )
    )

    if (
        slo_result["decision"] == "BLOCK"
        or budget_result[
            "release_action"
        ] == "BLOCK"
    ):
        decision = "BLOCK"

    elif (
        budget_result[
            "release_action"
        ]
        == "ALLOW_WITH_WARNING"
    ):
        decision = "ALLOW_WITH_WARNING"

    else:
        decision = "ALLOW"

    combined = {
        "deployment_revision": (
            args.deployment_revision
        ),
        "decision": decision,
        "slo_result": slo_result,
        "error_budget_result": (
            budget_result
        ),
    }

    output = Path(args.output)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            combined,
            indent=2,
        )
        + "\n"
    )

    print(
        json.dumps(
            combined,
            indent=2,
        )
    )

    if decision == "BLOCK":
        incident_gate = {
            **slo_result,
            "decision": "BLOCK",
        }

        incident = build_incident_report(
            deployment_revision=(
                args.deployment_revision
            ),
            gate_result=incident_gate,
            rollback_triggered=(
                args.rollback_triggered
            ),
            final_status=(
                args.final_status
            ),
            error_budget_result=(
                budget_result
            ),
        )

        json_path, md_path = (
            write_incident_artifacts(
                incident,
                args.incident_output_dir,
            )
        )

        print()
        print(
            f"Incident JSON: {json_path}"
        )
        print(
            f"Incident Markdown: {md_path}"
        )

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
