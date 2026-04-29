#!/usr/bin/env bash
set -euo pipefail

echo "=== Host Load ==="
uptime

echo "=== Memory ==="
free -h || true

echo "=== Disk ==="
df -h || true

echo "=== Python Processes ==="
ps -ef | grep python | grep -v grep || true
