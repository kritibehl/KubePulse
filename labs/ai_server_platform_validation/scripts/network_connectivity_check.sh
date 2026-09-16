#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-http://localhost:8000}"

echo "=== Ping localhost ==="
ping -c 3 localhost || true

echo "=== Curl target ==="
curl -v "$TARGET" || true

echo "=== Listening Ports ==="
ss -tuln || netstat -tuln || true

echo
echo "network_connectivity_check complete"
