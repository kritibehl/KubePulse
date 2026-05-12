from rollback.recommendation_engine import recommend_rollback


def test_recommend_rollback_blocks_on_canary_slo_alert_and_dependency_impact():
    canary = {
        "release_id": "release-102",
        "candidate": {"safe_to_operate": False},
        "delta": {
            "p95_latency_regression_percent": 608.34,
            "error_rate_delta": 0.08,
        },
    }

    topology = {
        "failure_root": "checkout",
        "impacted_services": ["inventory", "payments"],
    }

    alert = {"alert_triggered": True}

    result = recommend_rollback(canary, topology, alert)

    assert result["rollback_recommended"] is True
    assert result["release_decision"] == "block"
    assert result["rollback_candidate"] == "candidate_release"
    assert result["severity"] == "sev1"
    assert "p95_latency_regression" in result["blocked_rollout_reason"]
    assert "dependency_impact_detected" in result["blocked_rollout_reason"]
