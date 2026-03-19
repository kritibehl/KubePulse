#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-http://localhost:8081}"
COUNT="${2:-20}"

success=0
fail=0
times_file="$(mktemp)"

for i in $(seq 1 "$COUNT"); do
  result=$(curl -s -o /dev/null -w "%{http_code} %{time_total}" "$TARGET" || echo "000 5.000")
  code=$(echo "$result" | awk '{print $1}')
  time_total=$(echo "$result" | awk '{print $2}')
  echo "$time_total" >> "$times_file"

  if [ "$code" = "200" ]; then
    success=$((success+1))
  else
    fail=$((fail+1))
  fi
done

p50=$(sort -n "$times_file" | awk '{
  a[NR]=$1
}
END{
  if (NR==0) {print 0; exit}
  idx=int((NR+1)*0.50)
  if (idx<1) idx=1
  if (idx>NR) idx=NR
  print a[idx]
}')

p95=$(sort -n "$times_file" | awk '{
  a[NR]=$1
}
END{
  if (NR==0) {print 0; exit}
  idx=int((NR+1)*0.95)
  if (idx<1) idx=1
  if (idx>NR) idx=NR
  print a[idx]
}')

echo "target=$TARGET"
echo "count=$COUNT"
echo "success=$success"
echo "fail=$fail"
echo "p50_seconds=$p50"
echo "p95_seconds=$p95"

rm -f "$times_file"
