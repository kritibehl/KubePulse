#!/usr/bin/env python3
import json
import sys

def pct(new, old):
    if old == 0:
        return 0.0
    return round(((new - old) / old) * 100.0, 2)

if len(sys.argv) != 3:
    print("Usage: python scripts/kubepulse_compare.py baseline.json candidate.json")
    sys.exit(1)

with open(sys.argv[1]) as f:
    baseline = json.load(f)
with open(sys.argv[2]) as f:
    candidate = json.load(f)

p95 = pct(candidate.get("latency_p95_ms", 0.0), baseline.get("latency_p95_ms", 0.0))
err = round(candidate.get("error_rate", 0.0) - baseline.get("error_rate", 0.0), 4)
decision = "block" if p95 > 25 or err > 0.02 else "continue"

result = {
    "p95_latency_regression": f"+{p95}%",
    "error_rate_increase": f"+{round(err * 100, 2)}%",
    "decision": decision,
}

print(json.dumps(result, indent=2))
