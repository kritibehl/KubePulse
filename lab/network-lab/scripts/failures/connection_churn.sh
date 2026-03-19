#!/usr/bin/env bash
set -euo pipefail
CONTAINER="${1:-kp-api}"

docker exec "$CONTAINER" sh -c "apt-get update >/dev/null 2>&1 && apt-get install -y iproute2 iptables >/dev/null 2>&1 || true"
docker exec "$CONTAINER" sh -c "iptables -A OUTPUT -p tcp --dport 8080 -m statistic --mode random --probability 0.3 -j REJECT --reject-with tcp-reset"
echo "Applied intermittent TCP reset behavior to $CONTAINER"
