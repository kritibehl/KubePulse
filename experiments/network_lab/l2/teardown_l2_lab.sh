#!/usr/bin/env bash
set -euo pipefail

docker rm -f kubepulse-l2-lab >/dev/null 2>&1 || true

echo "PASS: Layer-2 lab removed"
