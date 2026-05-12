#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-localhost}"
PORT="${2:-8000}"

echo "=== Network Diagnostic ==="
echo "target=$TARGET port=$PORT"

echo
echo "=== Ping ==="
ping -c 3 "$TARGET" || true

echo
echo "=== Listening Ports ==="
ss -tuln || netstat -tuln || true

echo
echo "=== HTTP Check ==="
curl -v "http://${TARGET}:${PORT}/health" || true
