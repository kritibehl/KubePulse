#!/usr/bin/env bash
set -euo pipefail

docker rm -f kubepulse-netns-lab 2>/dev/null || true

echo "PASS: network lab removed"
