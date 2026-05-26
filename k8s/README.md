# Kubernetes Manifests

Raw Kubernetes deployment artifacts for KubePulse.

Includes:

- Deployment
- Service
- ConfigMap
- Secret
- HPA
- readiness probe
- liveness probe
- resource requests/limits

## Apply Example

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
Safe Scope

These are deployment-readiness artifacts for Kubernetes validation workflows.
