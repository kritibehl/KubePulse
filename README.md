# ⚙️ KubePulse

Kubernetes Chaos Engineering and Monitoring tool. Simulate faults and monitor system resilience using FastAPI and Prometheus.

## 📊 Grafana Dashboard

KubePulse comes with a pre-built Grafana dashboard to visualize CI/CD health metrics, including:

- 🔵 `pods_running` — number of active pods
- 🔴 `cluster_errors` — simulated or real-time error count
- 🟡 `chaos_mode` — indicates if chaos injection is active

## 🎯 Goals

- Inject simulated chaos into clusters
- Monitor container-level metrics
- Validate fault-tolerance strategies

## ▶️ Run Locally

```bash
uvicorn main:app --reload
```
