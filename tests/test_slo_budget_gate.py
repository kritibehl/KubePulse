from app.slo_budget_gate import evaluate_slo_gate


def test_slo_gate_blocks_latency_and_error_budget_violation():
    result = {
        "latency_p95_ms": 780.0,
        "latency_p99_ms": 1200.0,
        "error_rate": 0.08,
        "recovery_window_seconds": 12.0,
        "probes_say_healthy": True,
        "safe_to_operate": False,
    }

    gated = evaluate_slo_gate(result)

    assert gated["safe_to_operate"] is False
    assert gated["release_decision"] == "block"
    assert "p95_latency" in gated["violated_budgets"]
    assert "error_rate" in gated["violated_budgets"]
    assert "probe_mismatch_false_green" in gated["violated_budgets"]
    assert gated["rollback_review"] is True
