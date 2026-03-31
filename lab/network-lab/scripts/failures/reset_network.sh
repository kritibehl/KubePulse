#!/usr/bin/env bash
set -euo pipefail

for c in kp-edge kp-api kp-auth kp-router kp-ds-primary kp-ds-secondary; do
  docker exec "$c" sh -c "tc qdisc del dev eth0 root >/dev/null 2>&1 || true"
  docker exec "$c" sh -c "iptables -F >/dev/null 2>&1 || true"
done

for c in kp-edge kp-api kp-auth kp-router kp-ds-primary kp-ds-secondary; do
  docker network connect kpnet "$c" >/dev/null 2>&1 || true
done

echo "Reset network impairments"
