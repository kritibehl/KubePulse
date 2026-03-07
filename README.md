# KubePulse — Kubernetes Resilience Validation Framework

KubePulse is a Kubernetes resilience validation framework for running controlled disruption scenarios and measuring whether services recover correctly. It uses FastAPI, Prometheus, and Grafana to track recovery behavior, restart activity, and service health under failure.

## Grafana Dashboard

KubePulse includes a Grafana dashboard for visualizing resilience and cluster health signals, including:

- `pods_running` — number of active pods
- `cluster_errors` — simulated or observed error count
- `chaos_mode` — whether a disruption scenario is currently active

## Goals

- Run controlled disruption scenarios in Kubernetes environments
- Monitor service and container-level health signals
- Measure recovery behavior under failure
- Validate resilience and fault-tolerance strategies
- Detect misleading or incomplete health signals

## Run Locally

```bash
uvicorn main:app --reload