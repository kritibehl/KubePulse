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
from slo.evaluator import evaluate_slos


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate KubePulse release SLOs"
    )

    parser.add_argument(
        "--metrics",
        required=True,
        help="JSON file containing observed release metrics",
    )

    parser.add_argument(
        "--deployment-revision",
        required=True,
    )

    parser.add_argument(
        "--gate-output",
        default="artifacts/slo/gate_result.json",
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

    metrics = json.loads(
        Path(args.metrics).read_text()
    )

    result = evaluate_slos(metrics)

    gate_document = {
        "deployment_revision": args.deployment_revision,
        "observations": metrics,
        **result,
    }

    gate_path = Path(args.gate_output)
    gate_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    gate_path.write_text(
        json.dumps(gate_document, indent=2) + "\n"
    )

    print(json.dumps(gate_document, indent=2))

    if result["decision"] == "BLOCK":
        incident = build_incident_report(
            deployment_revision=args.deployment_revision,
            gate_result=result,
            rollback_triggered=args.rollback_triggered,
            final_status=args.final_status,
        )

        json_path, md_path = write_incident_artifacts(
            incident,
            args.incident_output_dir,
        )

        print()
        print(f"Incident JSON: {json_path}")
        print(f"Incident Markdown: {md_path}")

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
