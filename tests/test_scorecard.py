from app.resilience_scoring import compute_score

def test_restart_penalty():

    report = {
        "restart_count": 2,
        "recovery_window_seconds": 5,
        "readiness_false_positive": False
    }

    score = compute_score(report)

    assert score < 100
