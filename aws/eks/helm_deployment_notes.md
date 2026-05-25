# EKS Helm Deployment Notes

KubePulse can be packaged for EKS using the Helm chart in:

`helm/kubepulse/`

## Example

```bash
helm install kubepulse helm/kubepulse
Validation

After deployment:

kubectl get pods
kubectl get svc
kubectl port-forward svc/kubepulse 8000:80
make release-demo
Safe Scope

This documents an EKS deployment path using existing Kubernetes/Helm artifacts.
