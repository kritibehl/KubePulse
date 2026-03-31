#!/usr/bin/env bash
set -euo pipefail
docker exec kp-auth sh -c "apt-get update >/dev/null 2>&1 && apt-get install -y iproute2 >/dev/null 2>&1 || true"
docker exec kp-router sh -c "apt-get update >/dev/null 2>&1 && apt-get install -y iproute2 >/dev/null 2>&1 || true"
docker exec kp-auth sh -c "tc qdisc replace dev eth0 root netem delay 80ms"
docker exec kp-router sh -c "tc qdisc replace dev eth0 root netem delay 250ms"
echo "Applied asymmetric latency across auth and router hops"
