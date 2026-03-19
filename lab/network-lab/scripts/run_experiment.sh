#!/usr/bin/env bash
set -euo pipefail

SCENARIO="${1:-baseline}"

echo "Starting KubePulse Network Lab..."
docker compose -f lab/network-lab/docker-compose.yml up -d

sleep 3

case "$SCENARIO" in
  baseline)
    echo "Running baseline traffic"
    ;;
  dns_failure)
    bash lab/network-lab/scripts/failures/dns_failure.sh
    ;;
  latency)
    bash lab/network-lab/scripts/failures/latency_injection.sh kp-api 200ms 10%
    ;;
  partition)
    bash lab/network-lab/scripts/failures/partial_partition.sh kp-auth
    ;;
  churn)
    bash lab/network-lab/scripts/failures/connection_churn.sh kp-api
    ;;
  *)
    echo "Unknown scenario: $SCENARIO"
    exit 1
    ;;
esac

bash lab/network-lab/scripts/traffic/run_traffic.sh http://localhost:8081 25
