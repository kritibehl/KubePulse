#!/bin/bash
set -e

echo "Running KubePulse CI resilience pack"

curl -X POST http://127.0.0.1:8000/scenarios/run/cpu_stress
curl -X POST http://127.0.0.1:8000/scenarios/run/memory_stress
curl -X POST http://127.0.0.1:8000/scenarios/run/readiness_false_positive

curl http://127.0.0.1:8000/scorecards
