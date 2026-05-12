#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:-kubepulse}"
HEALTH_URL="${2:-http://localhost:8000/health}"

echo "=== Service Restart Guard ==="
echo "service=$SERVICE"
echo "health_url=$HEALTH_URL"

if curl -fsS "$HEALTH_URL" >/dev/null; then
  echo "OK service healthy; restart not required"
  exit 0
fi

echo "WARN health check failed; restart would be considered"
echo "recommended_action=inspect_logs_before_restart"
echo "guardrail=do_not_restart_if_active_release_gate_running"
