#!/usr/bin/env bash
set -euo pipefail
docker network disconnect kpnet kp-auth
echo "Disconnected kp-auth from kpnet"
