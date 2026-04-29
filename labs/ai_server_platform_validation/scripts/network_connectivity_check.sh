#!/usr/bin/env bash
set -euo pipefail

URL="${1:-http://127.0.0.1:8001/v1/models}
"

echo "Checking endpoint: $URL"
curl -fsS "$URL"
echo
echo "Endpoint reachable."
