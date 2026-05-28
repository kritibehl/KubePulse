from apple_quality_engineering.run_quality_matrix import evaluate_quality_matrix


def test_quality_matrix_all_cases_pass_and_block_expected_risks():
    report = evaluate_quality_matrix()

    assert report["cases_total"] == 5
    assert report["cases_passed"] == 5
    assert report["cases_failed"] == 0
    assert report["release_block_cases"] == 5


def test_quality_matrix_detects_regression_failure():
    cases = [
        {
            "feature": "release_gate",
            "edge_case": "safe_to_operate_false",
            "expected_behavior": "block",
            "regression_risk": "high",
            "ci_status": "pass",
            "observed_decision": "continue",
        }
    ]

    report = evaluate_quality_matrix(cases)

    assert report["cases_total"] == 1
    assert report["cases_failed"] == 1
