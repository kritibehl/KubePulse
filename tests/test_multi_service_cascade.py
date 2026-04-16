from app.multi_service_scenario import run_multi_service_failure
from app.topology_decision_lab import run_topology_decision_scenario


def test_multi_service_cascade_blocks_operation():
    result = run_multi_service_failure()

    assert result["scenario"] == "multi_service_cascade"
    assert result["readiness_false_positive"] is True
    assert result["safe_to_operate"] is False
    assert result["recommendation_action"] == "block"
    assert result["success"] is False
    assert result["latency_p95_ms"] > result["baseline_latency_p95_ms"]


def test_readiness_false_positive_is_not_safe():
    result = run_topology_decision_scenario("link_failure_failover")

    assert result["readiness_false_positive"] is True
    assert result["probes_say_healthy"] is True
    assert result["safe_to_operate"] is False
    assert result["recommendation_action"] in {"reroute", "block"}
    assert len(result["what_probes_missed"]) > 0
