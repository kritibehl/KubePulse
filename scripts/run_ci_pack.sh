#!/usr/bin/env bash
set -e

SCENARIOS=(
cpu_pressure
memory_pressure
pod_kill
dependency_timeout
packet_loss
)

for s in "${SCENARIOS[@]}"
do
  echo "Running scenario $s"
  curl -X POST http://127.0.0.1:8000/scenarios/run/$s
done
