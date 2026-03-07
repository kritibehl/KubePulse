<div align="center">

```
██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗
██║ ██╔╝██║   ██║██╔══██╗██╔════╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝
█████╔╝ ██║   ██║██████╔╝█████╗  ██████╔╝██║   ██║██║     ███████╗█████╗
██╔═██╗ ██║   ██║██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝
██║  ██╗╚██████╔╝██████╔╝███████╗██║     ╚██████╔╝███████╗███████║███████╗
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝
```

**Kubernetes Resilience Validation Framework**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.27+-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Prometheus](https://img.shields.io/badge/Prometheus-integrated-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-integrated-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com)
[![CI](https://img.shields.io/badge/CI-passing-22C55E?style=flat-square&logo=githubactions&logoColor=white)](.github/workflows/resilience-tests.yml)
[![License](https://img.shields.io/badge/License-MIT-6366F1?style=flat-square)](LICENSE)

*Validate recovery. Expose health-check blind spots. Ship with confidence.*

</div>

---

## The Problem

Production failures are often caused not by the disruption itself — but by **incorrect health signals masking degraded behavior**.

Traditional chaos engineering tools inject failures and stop there. They don't answer the questions that actually matter:

- Did the system **recover correctly**, or just appear to?
- Are your **readiness probes lying** to Kubernetes while requests fail?
- How long does recovery actually take **under real load**?
- Is your **latency regressing** after recovery compared to baseline?

KubePulse answers all of these.

---

## What is KubePulse?

KubePulse is a **resilience validation framework** for Kubernetes services. It executes controlled disruption scenarios, measures real service behavior, compares against a pre-disruption baseline, and produces structured scorecarded reports that expose reliability blind spots before they reach production.

```
Disruption → Metrics Probe → Baseline Comparison → Signal Validation → Scorecard → Report
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         KubePulse Platform                           │
│                                                                      │
│  ┌──────────────────┐    ┌───────────────────────────────────────┐   │
│  │  FastAPI          │    │           Validation Pipeline         │   │
│  │  Control Plane    │───▶│                                       │   │
│  │  app/main.py      │    │  ┌─────────────────────────────────┐  │   │
│  │                   │    │  │   Scenario Execution Engine      │  │   │
│  │  /health          │    │  │   app/chaos_injector.py          │  │   │
│  │  /scenarios/run/  │    │  │   inject_cpu_stress()            │  │   │
│  │  /scorecards      │    │  │   inject_memory_stress()         │  │   │
│  │  /scorecard/latest│    │  │   inject_readiness_false_pos()   │  │   │
│  │  /reports         │    │  └──────────────┬──────────────────┘  │   │
│  │  /reports/latest  │    │                 │                     │   │
│  │  /metrics         │    │  ┌──────────────▼──────────────────┐  │   │
│  └──────────────────┘    │  │   Real Metrics Probe             │  │   │
│                           │  │   app/metrics_probe.py           │  │   │
│                           │  │   probe_endpoint(url, n)         │  │   │
│                           │  │   p50 / p95 / p99 / error_rate   │  │   │
│                           │  └──────────────┬──────────────────┘  │   │
│                           │                 │                     │   │
│                           │  ┌──────────────▼──────────────────┐  │   │
│                           │  │   Baseline Comparison Engine     │  │   │
│                           │  │   app/baseline_compare.py        │  │   │
│                           │  │   drift % / error delta          │  │   │
│                           │  └──────────────┬──────────────────┘  │   │
│                           │                 │                     │   │
│                           │  ┌──────────────▼──────────────────┐  │   │
│                           │  │   Readiness Integrity Validator  │  │   │
│                           │  │   probe mismatch detection       │  │   │
│                           │  └──────────────┬──────────────────┘  │   │
│                           │                 │                     │   │
│                           │  ┌──────────────▼──────────────────┐  │   │
│                           │  │   Resilience Scorecard Engine    │  │   │
│                           │  │   pass/fail + recommendation     │  │   │
│                           │  └──────────────┬──────────────────┘  │   │
│                           └─────────────────┼─────────────────────┘   │
│                                             │                         │
│                  ┌──────────────────────────┼─────────────────┐       │
│                  ▼                          ▼                 ▼       │
│        ┌─────────────────┐    ┌──────────────────┐   ┌─────────────┐ │
│        │  Report Store   │    │  Markdown Report  │   │  Prometheus │ │
│        │  app/report_    │    │  Exporter         │   │  Exporter   │ │
│        │  store.py       │    │  app/report_      │   │  app/prom_  │ │
│        │  reports/*.json │    │  exporter.py      │   │  metrics.py │ │
│        └─────────────────┘    │  exports/*.md     │   │  /metrics   │ │
│                                └──────────────────┘   └─────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
          │                                            │
┌─────────▼──────────┐                    ┌───────────▼────────┐
│     Prometheus     │                    │       Grafana       │
└────────────────────┘                    └────────────────────┘
```

**Module reference:**

| Module | File | Responsibility |
|---|---|---|
| FastAPI Control Plane | `app/main.py` | API surface, pipeline orchestration |
| Scenario Execution Engine | `app/chaos_injector.py` | Stress commands, execution metadata |
| Metrics Probe | `app/metrics_probe.py` | Real HTTP request measurement — p50/p95/p99/error_rate |
| Baseline Comparison | `app/baseline_compare.py` | Healthy vs degraded drift analysis |
| Readiness Validator | *(integrated)* | Probe-signal mismatch detection |
| Scorecard Engine | *(integrated)* | Pass/fail evaluation + recommendations |
| Scenario Catalog Loader | `app/scenario_loader.py` | YAML scenario parsing |
| Report Store | `app/report_store.py` | Experiment artifact persistence |
| Markdown Exporter | `app/report_exporter.py` | JSON → human-readable reports |
| Prometheus Instrumentation | `app/prom_metrics.py` | Metrics endpoint for scraping |
| Sample Fault-Injectable Service | `sample_app/main.py` | Controlled degradation target |

---

## Scenario Catalog

Scenarios are defined declaratively as YAML in the `scenarios/` directory and loaded dynamically by `app/scenario_loader.py`.

```yaml
# scenarios/cpu_stress.yaml
name: cpu_stress
type: cpu_stress
target:
  namespace: default
  pod_name: demo-pod
execution:
  dry_run: true
thresholds:
  recovery_window_seconds_max: 15
  restart_count_max: 1
  readiness_false_positive_allowed: false
expected:
  status: pass
```

**Available scenarios:**

| Scenario | File | Description |
|---|---|---|
| `cpu_stress` | `scenarios/cpu_stress.yaml` | CPU starvation and thread contention |
| `cpu_pressure` | `scenarios/cpu_pressure.yaml` | Sustained CPU saturation |
| `memory_pressure` | `scenarios/memory_pressure.yaml` | Heap pressure and OOM-adjacent behavior |
| `readiness_false_positive` | `scenarios/readiness_false_positive.yaml` | Probe-signal mismatch detection |
| `packet_loss` | `scenarios/packet_loss.yaml` | Network instability and retry storms |
| `pod_kill` | `scenarios/pod_kill.yaml` | Pod termination and rescheduling |
| `dependency_timeout` | `scenarios/dependency_timeout.yaml` | Downstream dependency failure |

---

## Real Metrics Collection

KubePulse doesn't assume degradation — it measures it. `app/metrics_probe.py` sends real HTTP requests via `probe_endpoint(url, requests_count)` and computes:

| Metric | Description |
|---|---|
| `latency_p50_ms` | Median request latency |
| `latency_p95_ms` | 95th-percentile latency |
| `latency_p99_ms` | 99th-percentile latency |
| `error_rate` | Fraction of non-2xx responses |

---

## Baseline Comparison

`app/baseline_compare.py` captures a pre-disruption baseline then computes drift automatically during each scenario run.

```json
{
  "baseline_latency_p95_ms": 1.33,
  "observed_latency_p95_ms": 1.15,
  "latency_p95_drift_pct": -13.53,

  "baseline_error_rate": 0.0,
  "observed_error_rate": 0.02,
  "error_rate_delta": 0.02
}
```

No manual threshold configuration required.

---

## Readiness Integrity Validation

The most important capability in KubePulse — detecting **readiness false positives**: cases where Kubernetes marks a pod ready while the service is degraded.

```
Readiness before: ready
Readiness after:  ready          ← probe says healthy

Observed latency p95:  elevated
Observed error rate:   elevated  ← service is not healthy

Result:
  readiness_false_positive = true
  status                   = fail
```

When probes lie, Kubernetes routes traffic to broken pods and your dashboards show green. KubePulse surfaces this.

---

## Resilience Scorecards

Every scenario run generates a structured scorecard.

**CPU stress — passing run:**

```json
{
  "scenario": "cpu_stress",
  "status": "pass",
  "recovery_window_seconds": 8,
  "restart_count": 0,
  "probe_mismatch": false,
  "latency_p50_ms": 180,
  "latency_p95_ms": 210,
  "latency_p99_ms": 240,
  "error_rate": 0.02
}
```

**Readiness false positive — failing run:**

```json
{
  "scenario": "readiness_false_positive",
  "status": "fail",
  "recovery_window_seconds": 12,
  "restart_count": 0,
  "probe_mismatch": true,
  "readiness_before": "ready",
  "readiness_after": "ready",
  "readiness_false_positive": true,
  "latency_p50_ms": 0.92,
  "latency_p95_ms": 1.15,
  "latency_p99_ms": 1.19,
  "recommendation": "Tighten readiness checks to better reflect degraded service state."
}
```

Scorecards are stored as JSON in `reports/` and exported as Markdown summaries to `exports/`. Example artifact paths:

```
reports/readiness_false_positive_demo-pod_20260307T221620Z.json
exports/readiness_false_positive_demo-pod_20260307T201547Z.md
```

---

## Prometheus Observability

`app/prom_metrics.py` exposes resilience signals at `/metrics` for Prometheus scraping and Grafana visualization.

| Metric | Description |
|---|---|
| `kubepulse_scenarios_total` | Total executions by result |
| `kubepulse_latency_ms` | Observed latency histogram per scenario |
| `kubepulse_error_events` | Error count per scenario |
| `pods_running` | Active pod count during disruption |
| `cluster_errors` | Observed cluster error count |
| `chaos_mode` | Boolean — disruption scenario active |

---
## Reliability Signals Captured

KubePulse measures resilience through the following signals:

| Signal | Description |
|---|---|
| `recovery_window_seconds` | Time from disruption onset to stable recovery |
| `restart_count` | Container restarts during scenario |
| `latency_p50 / p95 / p99` | Request latency distribution under disruption |
| `error_rate` | Fraction of failed requests |
| `latency_drift_pct` | Deviation from baseline latency |
| `error_rate_delta` | Error rate change compared to baseline |
| `readiness_false_positive` | Probe signal mismatch detection |

## Sample Fault-Injectable Service

`sample_app/main.py` is a controlled degradation target for running experiments against a realistic service. Configure degradation state via environment variables:

```bash
# Inject artificial response latency
ARTIFICIAL_DELAY_MS=650

# Enable HTTP 500 error mode
ERROR_MODE=true

# Healthy baseline (default)
ARTIFICIAL_DELAY_MS=0 ERROR_MODE=false
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `POST` | `/scenarios/run/{scenario}` | Execute a named scenario |
| `GET` | `/scorecards` | List all scorecards |
| `GET` | `/scorecard/latest` | Latest scorecard |
| `GET` | `/reports` | List all experiment reports |
| `GET` | `/reports/latest` | Latest report |
| `GET` | `/metrics` | Prometheus metrics endpoint |

```bash
# Run CPU stress scenario
curl -X POST http://127.0.0.1:8000/scenarios/run/cpu_stress

# Run readiness false positive scenario
curl -X POST http://127.0.0.1:8000/scenarios/run/readiness_false_positive

# Get latest scorecard
curl http://127.0.0.1:8000/scorecard/latest

# Get latest report
curl http://127.0.0.1:8000/reports/latest

# Prometheus metrics
curl http://127.0.0.1:8000/metrics
```

---

## CI Integration

KubePulse ships with a GitHub Actions workflow that runs resilience validation automatically on every push and pull request.

```
.github/workflows/resilience-tests.yml
```

**Pipeline steps:** checkout → install dependencies → start sample service → start KubePulse → run scenarios → fetch and assert scorecards.

**Latest run: ✅ passing · ~15s · branch: master**

---

## Run Locally

```bash
# Install dependencies
pip install fastapi uvicorn requests prometheus-client pyyaml

# Start sample service (healthy baseline)
ARTIFICIAL_DELAY_MS=0 ERROR_MODE=false python3 -m uvicorn sample_app.main:app --host 127.0.0.1 --port 9000 &

# Start KubePulse
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Why KubePulse

> *"Your readiness probes are green. Your dashboards are green. Your users are getting errors."*

| | Traditional Chaos Tools | KubePulse |
|---|---|---|
| Failure injection | ✅ | ✅ |
| Recovery measurement | ❌ | ✅ |
| Health signal validation | ❌ | ✅ |
| Baseline comparison | ❌ | ✅ |
| Structured scorecards | ❌ | ✅ |
| Declarative scenario catalog | ❌ | ✅ |
| CI-automated validation | ❌ | ✅ |
| Experiment artifact store | ❌ | ✅ |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.11+ |
| API | FastAPI |
| Orchestration | Kubernetes |
| Stress tooling | `stress`, `tc netem` |
| Metrics | Prometheus |
| Visualization | Grafana |
| CI | GitHub Actions |
| Report formats | JSON, Markdown |

---

## Contributing

Contributions are welcome. To propose a new disruption scenario or validation capability, open an issue describing the failure class and what recovery behavior should be measured.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

*Built for engineers who need to know their systems recover correctly — not just that they survived.*

</div>