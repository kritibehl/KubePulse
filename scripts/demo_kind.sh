#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="kubepulse-demo"
PORT_FORWARD_PID=""

cleanup_port_forward() {
  if [[ -n "${PORT_FORWARD_PID}" ]]; then
    kill "${PORT_FORWARD_PID}" >/dev/null 2>&1 || true
  fi
}

trap cleanup_port_forward EXIT

for command in docker kind kubectl python3 curl; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    echo "Missing required command: ${command}"
    exit 1
  fi
done

echo
echo "==> Building demo API image"
docker build \
  -t kubepulse-demo-api:local \
  demo

if kind get clusters | grep -qx "${CLUSTER_NAME}"; then
  echo
  echo "==> Removing previous ${CLUSTER_NAME} cluster"
  kind delete cluster --name "${CLUSTER_NAME}"
fi

echo
echo "==> Creating Kind cluster"
kind create cluster \
  --name "${CLUSTER_NAME}" \
  --image kindest/node:v1.31.0 \
  --config demo/kind-cluster.yaml \
  --wait 120s

echo
echo "==> Loading local API image into Kind"
kind load docker-image \
  kubepulse-demo-api:local \
  --name "${CLUSTER_NAME}"

echo
echo "==> Deploying API and PostgreSQL"
kubectl apply -f demo/k8s.yaml

kubectl rollout status deployment/postgres --timeout=120s
kubectl rollout status deployment/kubepulse-demo-api --timeout=120s

echo
echo "==> Starting API port-forward"
kubectl port-forward \
  service/kubepulse-demo-api \
  18080:8080 \
  >/tmp/kubepulse-port-forward.log 2>&1 &

PORT_FORWARD_PID=$!

for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:18080/health >/dev/null; then
    break
  fi

  sleep 1
done

echo
echo "=================================================="
echo "BASELINE: dependency reachable"
echo "=================================================="

python3 scripts/release_gate.py \
  --output reports/demo_kind_baseline_gate.json \
  --expected-decision ALLOW

echo
echo "==> Injecting PostgreSQL connectivity failure"
echo "    PostgreSQL pod remains running."
echo "    Service selector is changed so the API cannot reach it."

kubectl patch service postgres \
  --type merge \
  -p '{"spec":{"selector":{"app":"postgres-unreachable"}}}'

sleep 5

echo
echo "=================================================="
echo "FAILURE: HTTP health and pod readiness stay green"
echo "=================================================="

curl -sS http://127.0.0.1:18080/health
echo

kubectl get pods \
  -l app=kubepulse-demo-api \
  -o custom-columns=NAME:.metadata.name,READY:.status.containerStatuses[0].ready,STATUS:.status.phase

echo
echo "=================================================="
echo "KUBEPULSE RELEASE-GATE DECISION"
echo "=================================================="

python3 scripts/release_gate.py \
  --output reports/demo_kind_blocked_gate.json \
  --expected-decision BLOCK

echo
echo "==> Rolling back PostgreSQL service selector"

kubectl patch service postgres \
  --type merge \
  -p '{"spec":{"selector":{"app":"postgres"}}}'

sleep 5

echo
echo "=================================================="
echo "POST-ROLLBACK VERIFICATION"
echo "=================================================="

python3 scripts/release_gate.py \
  --output reports/demo_kind_rollback_gate.json \
  --expected-decision ALLOW

echo
echo "RESULT: PASS"
echo
echo "Generated artifacts:"
echo "  reports/demo_kind_baseline_gate.json"
echo "  reports/demo_kind_blocked_gate.json"
echo "  reports/demo_kind_rollback_gate.json"
echo
echo "Run 'make demo-kind-clean' to remove the cluster."
