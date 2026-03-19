#!/usr/bin/env bash
set -euo pipefail
CONTAINER="${1:-kp-api}"
DELAY="${2:-200ms}"
LOSS="${3:-10%}"

docker exec "$CONTAINER" sh -c "apt-get update >/dev/null 2>&1 && apt-get install -y iproute2 >/dev/null 2>&1 || true"
docker exec "$CONTAINER" sh -c "tc qdisc replace dev eth0 root netem delay $DELAY loss $LOSS"
echo "Applied netem delay=$DELAY loss=$LOSS to $CONTAINER"
