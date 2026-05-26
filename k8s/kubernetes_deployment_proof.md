# Kubernetes Deployment Proof

KubePulse includes raw Kubernetes and Helm deployment artifacts.

## Deployment Proof Checklist

| Capability | Artifact |
|---|---|
| Deployment YAML | `k8s/deployment.yaml` |
| Service manifest | `k8s/service.yaml` |
| HPA autoscaling | `k8s/hpa.yaml` |
| ConfigMap | `k8s/configmap.yaml` |
| Secret | `k8s/secret.yaml` |
| Readiness probe | `k8s/deployment.yaml` |
| Liveness probe | `k8s/deployment.yaml` |
| Helm chart | `helm/kubepulse/` |

## Release-Safety Relevance

These artifacts make KubePulse deployable as a Kubernetes release-validation service with health checks, configuration, secrets, resource limits, and autoscaling controls.
