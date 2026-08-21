import json
from pathlib import Path

import pytest

from reliability.error_budget import evaluate_error_budget


FIXTURES = Path("tests/fixtures")


def load(name: str):
    return json.loads(
        (FIXTURES / name).read_text()
    )


def test_normal_burn_allows_release():
    result = evaluate_error_budget(
        load("burn_normal.json")
    )

    assert result["burn_status"] == "NORMAL"
    assert result["release_action"] == "ALLOW"

    assert result["cumulative"][
        "budget_consumed_percent"
    ] == pytest.approx(30.0)

    assert result["cumulative"][
        "budget_remaining_percent"
    ] == pytest.approx(70.0)


def test_elevated_burn_warns():
    result = evaluate_error_budget(
        load("burn_elevated.json")
    )

    assert result["burn_status"] == "ELEVATED"
    assert (
        result["release_action"]
        == "ALLOW_WITH_WARNING"
    )

    assert result["windows"]["1h"]["burn_rate"] == pytest.approx(
        1.5
    )


def test_fast_multi_window_burn_blocks():
    result = evaluate_error_budget(
        load("burn_fast.json")
    )

    assert result["burn_status"] == "FAST_BURN"
    assert result["release_action"] == "BLOCK"

    assert result["windows"]["1h"]["burn_rate"] == pytest.approx(
        6.0
    )

    assert result["windows"]["6h"]["burn_rate"] == pytest.approx(
        3.0
    )


def test_exhausted_budget_blocks():
    result = evaluate_error_budget(
        load("burn_exhausted.json")
    )

    assert result["burn_status"] == "BUDGET_EXHAUSTED"
    assert result["release_action"] == "BLOCK"

    assert result["cumulative"][
        "budget_consumed_percent"
    ] == pytest.approx(300.0)

    assert result["cumulative"][
        "budget_remaining_percent"
    ] == pytest.approx(0.0)


def test_invalid_request_counts_fail():
    with pytest.raises(ValueError):
        evaluate_error_budget(
            {
                "availability_slo_percent": 99.9,
                "cumulative": {
                    "requests": 10,
                    "errors": 11,
                },
                "windows": {
                    "1h": {
                        "requests": 100,
                        "errors": 0,
                    }
                },
            }
        )
