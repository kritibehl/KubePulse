#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${KUBEPULSE_BASE_URL:-http://127.0.0.1:8000}"
curl -s "${BASE_URL}/scenarios"
echo
