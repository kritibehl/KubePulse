from incident_reporting.generator import build_incident_report
from slo.evaluator import evaluate_slos


def test_good_release_is_allowed():
    result = evaluate_slos(
        {
            "availability_percent": 99.97,
            "p95_latency_ms": 184,
            "error_rate_percent": 0.3,
            "recovery_time_seconds": 29,
        }
    )

    assert result["decision"] == "ALLOW"
    assert result["safe_to_release"] is True
    assert result["failed_slo_count"] == 0


def test_latency_violation_blocks_release():
    result = evaluate_slos(
        {
            "availability_percent": 99.97,
            "p95_latency_ms": 780,
            "error_rate_percent": 0.3,
            "recovery_time_seconds": 29,
        }
    )

    assert result["decision"] == "BLOCK"

    assert [
        item["metric"]
        for item in result["violations"]
    ] == ["p95_latency_ms"]


def test_multiple_violations_are_preserved():
    result = evaluate_slos(
        {
            "availability_percent": 98.8,
            "p95_latency_ms": 860,
            "error_rate_percent": 4.2,
            "recovery_time_seconds": 74,
        }
    )

    assert result["decision"] == "BLOCK"
    assert result["failed_slo_count"] == 4


def test_missing_metric_fails_closed():
    result = evaluate_slos(
        {
            "availability_percent": 99.99,
            "p95_latency_ms": 100,
            "error_rate_percent": 0.1,
        }
    )

    assert result["decision"] == "BLOCK"

    violation = result["violations"][0]

    assert violation["metric"] == "recovery_time_seconds"
    assert violation["status"] == "MISSING"


def test_incident_uses_slo_evidence():
    result = evaluate_slos(
        {
            "availability_percent": 99.94,
            "p95_latency_ms": 780,
            "error_rate_percent": 0.7,
            "recovery_time_seconds": 29,
        }
    )

    incident = build_incident_report(
        deployment_revision="candidate-v2",
        gate_result=result,
        rollback_triggered=True,
        final_status="healthy",
    )

    assert incident["release_decision"] == "BLOCK"
    assert incident["violated_slo"] == "p95_latency_ms"
    assert incident["observed_value"] == 780
    assert incident["threshold"] == 300
    assert incident["rollback_triggered"] is True
    assert incident["recovery_seconds"] == 29
    assert incident["final_status"] == "healthy"
