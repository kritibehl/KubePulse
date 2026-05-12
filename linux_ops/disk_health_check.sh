#!/usr/bin/env bash
set -euo pipefail

THRESHOLD="${DISK_THRESHOLD_PERCENT:-85}"

echo "=== Disk Health Check ==="
df -h

echo
echo "=== Threshold Check ==="
df -P | awk -v threshold="$THRESHOLD" '
NR > 1 {
  usage=$5
  gsub("%", "", usage)
  if (usage+0 >= threshold) {
    print "ALERT disk_usage_high filesystem="$6" usage="usage"% threshold="threshold"%"
    found=1
  }
}
END {
  if (!found) print "OK disk usage below threshold"
}'
