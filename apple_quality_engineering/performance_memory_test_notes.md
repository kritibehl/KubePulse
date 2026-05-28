# Performance and Memory Test Notes

## Performance Signals

KubePulse tracks:
- p95 latency
- p99 latency
- error rate
- queue depth
- autoscaling recovery time
- replica count

## Memory/Resource Notes

Deployment artifacts include:
- Kubernetes resource requests
- Kubernetes resource limits
- HPA scaling thresholds
- capacity validation reports

## Release Impact

Performance or resource regression can block rollout continuation.
