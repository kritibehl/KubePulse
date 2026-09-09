# Cilium + Hubble Live Topology Validation

KubePulse includes a controlled Kubernetes datapath-observability experiment using Kind, Cilium and Hubble.

## Environment

- Kubernetes: Kind / Kubernetes v1.34.3
- CNI: Cilium v1.20.0
- Observability: Hubble + Hubble Relay
- Host architecture: Apple Silicon / arm64
- Workload: client -> Kubernetes Service -> server
- Traffic: 20 deterministic HTTP requests

## Validation

The experiment validates:

1. Kubernetes API liveness and readiness.
2. Cilium agent and operator readiness.
3. Hubble Relay availability.
4. Kubernetes Service reachability through the Cilium datapath.
5. Successful application traffic.
6. Hubble observation of workload network flows.

The experiment is a controlled local Kubernetes lab and is not presented as production-cluster operating experience.

## Evidence

- `artifacts/argo_hubble_e2e/topology-live/kind-config.yaml`
- `artifacts/argo_hubble_e2e/topology-live/workloads.yaml`
- `artifacts/argo_hubble_e2e/topology-live/summary.json`
- `artifacts/argo_hubble_e2e/topology-live/hubble_status.txt`
- `artifacts/argo_hubble_e2e/topology-live/hubble_flows.jsonl`
- `artifacts/argo_hubble_e2e/topology-live/workload_state.txt`
- `artifacts/argo_hubble_e2e/topology-live/traffic_results.txt`
- `artifacts/argo_hubble_e2e/topology-live/image_architecture.txt`

## Result

A PASS requires all deterministic client requests to succeed and Hubble to observe network-flow records from the validation namespace.
