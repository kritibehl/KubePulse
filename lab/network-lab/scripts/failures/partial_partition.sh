#!/usr/bin/env bash
set -euo pipefail
CONTAINER="${1:-kp-auth}"
docker network disconnect kpnet "$CONTAINER"
echo "Disconnected $CONTAINER from kpnet"
