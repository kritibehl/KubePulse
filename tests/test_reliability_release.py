import json
from pathlib import Path

from incident_reporting.generator import (
    build_incident_report,
)
from reliability.error_budget import (
    evaluate_error_budget,
)
from slo.evaluator import evaluate_slos


FIXTURES = Path("tests/fixtures")


def load(name: str):
    return json.loads(
        (FIXTURES / name).read_text()
    )


def test_fast_burn_can_block_even_when_point_slos_pass():
    slo = evaluate_slos(
        load("slo_good.json")
    )

    budget = evaluate_error_budget(
        load("burn_fast.json")
    )

    assert slo["decision"] == "ALLOW"
    assert budget["release_action"] == "BLOCK"
    assert budget["burn_status"] == "FAST_BURN"


def test_incident_contains_error_budget_evidence():
    slo = evaluate_slos(
        load("slo_good.json")
    )

    budget = evaluate_error_budget(
        load("burn_fast.json")
    )

    incident_gate = {
        **slo,
        "decision": "BLOCK",
    }

    incident = build_incident_report(
        deployment_revision="candidate-fast-burn-v3",
        gate_result=incident_gate,
        rollback_triggered=True,
        final_status="healthy",
        error_budget_result=budget,
    )

    assert incident[
        "violation_type"
    ] == "error_budget"

    assert incident[
        "burn_status"
    ] == "FAST_BURN"

    assert incident[
        "burn_rates"
    ]["1h"] == 6.0

    assert incident[
        "burn_rates"
    ]["6h"] == 3.0

    assert incident[
        "error_budget"
    ][
        "budget_remaining_percent"
    ] == 30.0
