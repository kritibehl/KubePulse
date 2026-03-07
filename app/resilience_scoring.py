
def compute_score(report):

    score = 100

    if report["restart_count"] > 0:
        score -= 20

    if report["recovery_window_seconds"] > 20:
        score -= 30

    if report.get("readiness_false_positive"):
        score -= 40

    score = max(score, 0)

    return score
