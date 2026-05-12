#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-reports/incident_snapshot}"
mkdir -p "$OUT_DIR"

echo "=== Capturing incident snapshot into $OUT_DIR ==="

{
  echo "timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "hostname=$(hostname)"
  echo "uptime=$(uptime)"
} > "$OUT_DIR/system_summary.txt"

df -h > "$OUT_DIR/disk.txt" || true
ps aux > "$OUT_DIR/processes.txt" || true
(ss -tuln || netstat -tuln || true) > "$OUT_DIR/ports.txt"
curl -s http://localhost:8000/health > "$OUT_DIR/kubepulse_health.json" || true
curl -s http://localhost:8000/metrics > "$OUT_DIR/kubepulse_metrics.txt" || true

echo "snapshot_status=created"
echo "snapshot_dir=$OUT_DIR"
