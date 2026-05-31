import json

def calculate_burn_rate(p95_latency_ms=620, error_rate=0.05, dependency_risk_score=91):
    fast_burn = p95_latency_ms > 250 or error_rate > 0.02 or dependency_risk_score > 80
    return {
        "slo": "99.9",
        "error_budget_remaining": "4.2%",
        "fast_burn_detected": fast_burn,
        "p95_latency_ms": p95_latency_ms,
        "error_rate": error_rate,
        "dependency_risk_score": dependency_risk_score
    }

if __name__ == "__main__":
    print(json.dumps(calculate_burn_rate(), indent=2))
