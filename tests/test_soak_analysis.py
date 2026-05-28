from soak_testing.run_soak_analysis import analyze_soak


def test_soak_analysis_blocks_long_duration_drift():
    data = {
        "scenarios": [
            {
                "duration": "24h",
                "latency_p95_start_ms": 200,
                "latency_p95_end_ms": 700,
                "error_count_start": 0,
                "error_count_end": 150,
                "resource_pressure": "high",
                "status": "block",
            }
        ]
    }

    report = analyze_soak(data)

    assert report["soak_runs"] == 1
    assert report["blocked_runs"] == 1
    assert report["results"][0]["release_decision"] == "block"


def test_soak_analysis_allows_stable_short_run():
    data = {
        "scenarios": [
            {
                "duration": "1h",
                "latency_p95_start_ms": 220,
                "latency_p95_end_ms": 240,
                "error_count_start": 0,
                "error_count_end": 2,
                "resource_pressure": "low",
                "status": "pass",
            }
        ]
    }

    report = analyze_soak(data)

    assert report["soak_runs"] == 1
    assert report["blocked_runs"] == 0
    assert report["results"][0]["release_decision"] == "continue"
