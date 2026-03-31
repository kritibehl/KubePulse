#!/usr/bin/env bash
set -euo pipefail
docker network disconnect kpnet kp-ds-primary
echo "Disconnected datastore primary from kpnet"
