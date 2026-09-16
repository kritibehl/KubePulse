#!/usr/bin/env bash
set -euo pipefail

echo "=== Host Load ==="
uptime || true

echo "=== Memory ==="
free -h || true

echo "=== Disk ==="
df -h || true

echo "=== AMD GPU / ROCm ==="
rocm-smi || true

echo "=== AMD PCI Devices ==="
lspci | grep -i amd || true

echo "=== Listening Ports ==="
ss -tuln || netstat -tuln || true

echo "=== KubePulse Health ==="
curl -s http://localhost:8000/health || true

echo
echo "platform_health_check complete"
