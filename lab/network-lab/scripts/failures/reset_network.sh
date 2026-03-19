#!/usr/bin/env bash
set -euo pipefail

for c in kp-api kp-auth kp-edge kp-datastore; do
  docker exec "$c" sh -c "tc qdisc del dev eth0 root >/dev/null 2>&1 || true"
  docker exec "$c" sh -c "iptables -F >/dev/null 2>&1 || true"
done

for c in kp-auth kp-api kp-edge kp-datastore; do
  docker network connect kpnet "$c" >/dev/null 2>&1 || true
done

echo "Reset network impairments"
