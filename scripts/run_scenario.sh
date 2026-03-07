#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: ./scripts/run_scenario.sh <scenario_name>"
  exit 1
fi

SCENARIO_NAME="$1"
BASE_URL="${KUBEPULSE_BASE_URL:-http://127.0.0.1:8000}"

echo "Running scenario: ${SCENARIO_NAME}"
echo

curl -s -X POST "${BASE_URL}/scenarios/run/${SCENARIO_NAME}"
echo
echo

echo "Latest scorecard:"
curl -s "${BASE_URL}/scorecard/latest"
echo
