from scenarios.postgres_dependency_degradation import run_postgres_dependency_degradation


def test_postgres_dependency_false_green_blocks_release():
    report = run_postgres_dependency_degradation()

    assert report["app_health_status"] == 200
    assert report["app_health_passed"] is True
    assert report["postgres_reachable"] is False
    assert report["readiness_probe_status"] == "ready"
    assert report["dependency_readiness_status"] == "failed"
    assert report["readiness_mismatch"] is True
    assert report["false_green_database_backed_service"] is True
    assert report["safe_to_operate"] is False
    assert report["release_decision"] == "block"


def test_postgres_dependency_scorecard_contains_release_readiness():
    report = run_postgres_dependency_degradation()

    assert report["scorecard"]["service_health"] == "pass"
    assert report["scorecard"]["postgres_dependency"] == "fail"
    assert report["scorecard"]["latency_budget"] == "fail"
    assert report["scorecard"]["probe_integrity"] == "fail"
    assert report["scorecard"]["release_readiness"] == "block"
