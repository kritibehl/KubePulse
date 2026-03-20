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
[![Prometheus](https://img.shields.io/badge/Prometheus-implemented-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-ready-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com)
[![CI](https://img.shields.io/badge/CI-passing-22C55E?style=flat-square&logo=githubactions&logoColor=white)](.github/workflows/resilience-tests.yml)
[![License](https://img.shields.io/badge/License-MIT-6366F1?style=flat-square)](LICENSE)

*Automated resilience validation for Kubernetes — measure recovery behavior, detect probe-signal blind spots, and surface reliability regressions before production.*

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

KubePulse is a **resilience validation framework** for Kubernetes services. It executes controlled disruption scenarios, measures real service behavior, compares against a pre-disruption baseline, computes a composite resilience score, and produces structured scorecarded reports that expose reliability blind spots before they reach production.

```
Scenario YAML → Chaos Injector → Metrics Probe → Baseline Comparison
      → Readiness Validation → Resilience Score → Scorecard → Report
```

---

## Project Structure

```
KubePulse/
│
├── app/
│   ├── main.py                   # FastAPI control plane
│   ├── chaos_injector.py         # Scenario execution engine
│   ├── scenario_runner.py        # Orchestrates execution pipeline
│   ├── scenario_loader.py        # YAML scenario catalog loader
│   ├── metrics_probe.py          # Real request metrics collection
│   ├── baseline_compare.py       # Baseline vs degraded comparison
│   ├── resilience_score.py       # Composite resilience scoring
│   ├── prom_metrics.py           # Prometheus instrumentation
│   ├── report_store.py           # Experiment artifact persistence
│   └── report_exporter.py        # Markdown report exporter
│
├── scenarios/
│   ├── cpu_stress.yaml
│   ├── cpu_pressure.yaml
│   ├── memory_pressure.yaml
│   ├── readiness_false_positive.yaml
│   ├── packet_loss.yaml
│   ├── pod_kill.yaml
│   └── dependency_timeout.yaml
│
├── sample_app/
│   └── main.py                   # Fault-injectable test service
│
├── lab/
│   └── network-lab/
│       ├── docker-compose.yml
│       └── scripts/run_experiment.sh
│
├── reports/                      # JSON experiment artifacts
├── exports/                      # Markdown resilience summaries
│
└── .github/workflows/
    └── resilience-tests.yml
```

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                          KubePulse Platform                           │
│                                                                       │
│  ┌───────────────────┐    ┌────────────────────────────────────────┐  │
│  │  FastAPI           │    │            Validation Pipeline         │  │
│  │  Control Plane     │───▶│                                        │  │
│  │  app/main.py       │    │  ┌──────────────────────────────────┐  │  │
│  │                    │    │  │  Scenario Loader                  │  │  │
│  │  /health           │    │  │  app/scenario_loader.py           │  │  │
│  │  /scenarios        │    │  └──────────────┬───────────────────┘  │  │
│  │  /scenarios/run/   │    │                 │                      │  │
│  │  /scorecard/latest │    │  ┌──────────────▼───────────────────┐  │  │
│  │  /scorecards       │    │  │  Chaos Injector                   │  │  │
│  │  /reports          │    │  │  app/chaos_injector.py            │  │  │
│  │  /reports/latest   │    │  └──────────────┬───────────────────┘  │  │
│  │  /reports/export/  │    │                 │                      │  │
│  │  /metrics          │    │  ┌──────────────▼───────────────────┐  │  │
│  └───────────────────┘    │  │  Real Metrics Probe               │  │  │
│                            │  │  p50 / p95 / p99 / error_rate     │  │  │
│                            │  └──────────────┬───────────────────┘  │  │
│                            │                 │                      │  │
│                            │  ┌──────────────▼───────────────────┐  │  │
│                            │  │  Baseline Comparison Engine       │  │  │
│                            │  │  latency drift % / error delta    │  │  │
│                            │  └──────────────┬───────────────────┘  │  │
│                            │                 │                      │  │
│                            │  ┌──────────────▼───────────────────┐  │  │
│                            │  │  Readiness Integrity Validator    │  │  │
│                            │  │  probe mismatch detection         │  │  │
│                            │  └──────────────┬───────────────────┘  │  │
│                            │                 │                      │  │
│                            │  ┌──────────────▼───────────────────┐  │  │
│                            │  │  Resilience Score Engine          │  │  │
│                            │  │  composite score / sub-scores     │  │  │
│                            │  └──────────────┬───────────────────┘  │  │
│                            └─────────────────┼──────────────────────┘  │
│                                              │                         │
│               ┌──────────────────────────────┼──────────────────┐      │
│               ▼                              ▼                  ▼      │
│     ┌──────────────────┐      ┌──────────────────┐    ┌───────────────┐│
│     │  Report Store    │      │  Markdown Report  │    │  Prometheus   ││
│     │  reports/*.json  │      │  exports/*.md     │    │  /metrics     ││
│     └──────────────────┘      └──────────────────┘    └───────┬───────┘│
└────────────────────────────────────────────────────────────────┼────────┘
                                                                 │
                                                     ┌───────────▼──────────┐
                                                     │  Prometheus scraping  │
                                                     │  Grafana-compatible   │
                                                     └──────────────────────┘
```

---

## Scenario Catalog

Scenarios are defined declaratively as YAML in `scenarios/` and loaded dynamically by `app/scenario_loader.py`. The framework is extensible without code changes.

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

| Scenario | Description |
|---|---|
| `cpu_stress` | CPU starvation and thread contention |
| `cpu_pressure` | Sustained CPU saturation |
| `memory_pressure` | Heap pressure and OOM-adjacent behavior |
| `readiness_false_positive` | Probe-signal mismatch detection |
| `packet_loss` | Network instability and retry storms |
| `pod_kill` | Pod termination and rescheduling |
| `dependency_timeout` | Downstream dependency failure |

---

## Network-Aware Resilience Validation

KubePulse includes network disruption scenarios as first-class validation primitives:

- Packet loss
- DNS resolution failure
- Service-to-service latency injection
- Node-to-node partition
- Dropped egress / degraded ingress
- MTU mismatch simulation
- Intermittent TCP resets
- Connection churn

### What KubePulse Measures (Network Runs)

- DNS success rate
- TCP connect latency
- HTTP success rate under degraded network conditions
- Cross-zone / cross-node communication degradation
- Path recovery time
- Readiness false positives vs. real network availability
- Latency percentile drift and error-rate delta relative to baseline

### Example: DNS Failure — Baseline vs Degraded

| Metric | Baseline | Degraded | Delta |
|---|---:|---:|---:|
| Network health score | 95 | 53 | −42 |
| DNS success rate | 98.5% | 55.0% | −43.5 pts |
| TCP connect latency | 18 ms | 145 ms | +127 ms |
| HTTP success rate | 99.0% | 72.0% | −27.0 pts |
| p95 latency | 165 ms | 315 ms | +150 ms |
| Error rate | 1.0% | 8.0% | +7.0 pts |
| Recovery window | 5 s | 14 s | +9 s |
| Readiness false positives | 0 | 2 | +2 |
| Recommendation confidence | 0.88 | 0.93 | +0.05 |

---

## Real Metrics Collection

KubePulse measures actual degradation rather than assuming it. `app/metrics_probe.py` sends real HTTP requests to the service under test and computes:

| Metric | Description |
|---|---|
| `latency_p50_ms` | Median request latency |
| `latency_p95_ms` | 95th-percentile latency |
| `latency_p99_ms` | 99th-percentile latency |
| `error_rate` | Fraction of non-2xx responses |

---

## Baseline Comparison

`app/baseline_compare.py` captures a pre-disruption baseline and computes drift automatically — no manual threshold configuration required.

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

---

## Readiness Integrity Validation

KubePulse detects **readiness false positives** — cases where Kubernetes marks a pod ready while the service is actually degraded.

```
Readiness before: ready
Readiness after:  ready          ← probe says healthy

Observed latency p95:  elevated
Observed error rate:   elevated  ← service is not healthy

Result:
  readiness_false_positive = true
  status                   = fail
```

When probes lie, Kubernetes routes traffic to broken pods and dashboards show green. KubePulse surfaces this.

---

## Resilience Scoring

`app/resilience_score.py` converts raw experiment results into a **composite resilience score** across four independent dimensions:

| Sub-score | Factor |
|---|---|
| `recovery_score` | How quickly the system returned to stable state |
| `latency_score` | Latency stability under and after disruption |
| `error_score` | Error rate during the disruption window |
| `probe_integrity_score` | Accuracy of readiness probe signals |

**Example — CPU stress run:**

```json
{
  "resilience_score": 86,
  "recovery_score": 90,
  "latency_score": 80,
  "error_score": 75,
  "probe_integrity_score": 100
}
```

A score of 100 means the system recovered correctly with accurate health signals and no regressions. Lower scores expose which dimension failed and by how much, enabling comparison across services and scenarios.

---

## Resilience Scorecards

Every scenario run produces a full structured scorecard.

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
  "error_rate": 0.02,
  "resilience_score": 86
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

Scorecards are stored as JSON in `reports/` and exported as Markdown to `exports/`:

```
reports/cpu_stress_demo-pod_20260307T224036Z.json
exports/readiness_false_positive_demo-pod_20260307T201547Z.md
```

---

## Dependency-Path Diagnostics

For network degradation scenarios, KubePulse infers a lightweight service dependency graph and emits:

- Upstream/downstream relationship hints
- Latency/error propagation path
- Likely root-cause service or network segment
- Estimated blast radius across impacted services

**Example dependency path:**
```
frontend → auth-service → shared-db
```

---

## Auto-Remediation Recommendations

After each run, KubePulse emits a recommendation bundle:

- Probable source of degradation
- Suggested action: `restart`, `reroute`, `scale`, or `isolate`
- Confidence score
- Suggested rollback or config-change note

---

## Prometheus Integration

`app/prom_metrics.py` instruments KubePulse with `prometheus-client` and exposes a scrape endpoint at `GET /metrics`.

| Metric | Description |
|---|---|
| `kubepulse_scenarios_total` | Total executions by result |
| `kubepulse_latency_ms` | Observed latency histogram per scenario |
| `kubepulse_error_events` | Error count per scenario |
| `pods_running` | Active pod count during disruption |
| `cluster_errors` | Observed cluster error count |
| `chaos_mode` | Boolean — disruption scenario active |

All metrics are Grafana-ready and visualizable using any Prometheus datasource.

---

## Sample Fault-Injectable Service

`sample_app/main.py` is a controlled degradation target for running experiments. Configure via environment variables:

```bash
# Healthy baseline
ARTIFICIAL_DELAY_MS=0 ERROR_MODE=false

# Latency degradation
ARTIFICIAL_DELAY_MS=650

# Error mode
ERROR_MODE=true
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/scenarios` | List available scenarios |
| `GET` | `/scenarios/{name}` | Get scenario config |
| `POST` | `/scenarios/run/{name}` | Execute a named scenario |
| `GET` | `/scorecard/latest` | Latest scorecard |
| `GET` | `/scorecards` | List all scorecards |
| `GET` | `/reports` | List all experiment reports |
| `GET` | `/reports/latest` | Latest report |
| `GET` | `/reports/export/latest` | Export latest report as Markdown |
| `GET` | `/metrics` | Prometheus metrics endpoint |

```bash
# Run CPU stress scenario
curl -X POST http://127.0.0.1:8000/scenarios/run/cpu_stress

# Run readiness false positive scenario
curl -X POST http://127.0.0.1:8000/scenarios/run/readiness_false_positive

# Get latest scorecard
curl http://127.0.0.1:8000/scorecard/latest

# Export latest report as Markdown
curl http://127.0.0.1:8000/reports/export/latest

# Prometheus metrics
curl http://127.0.0.1:8000/metrics
```

---

## CI Integration

KubePulse ships with a GitHub Actions workflow that runs resilience validation automatically on every push and pull request.

```
.github/workflows/resilience-tests.yml
```

**Pipeline:** checkout → install dependencies → start sample service → start KubePulse → run scenarios → fetch and assert scorecards.

**Latest run: ✅ passing · ~15s · branch: master**

---

## Network Lab

KubePulse includes a Linux namespace/container-based network lab for repeatable service-to-service resilience experiments under controlled network degradation.

```
lab/network-lab/
├── docker-compose.yml
└── scripts/run_experiment.sh
```

**Supported scenarios:** `baseline`, `dns_failure`, `latency`, `partition`, `churn`

See [`docs/network-lab/README.md`](docs/network-lab/README.md) for full documentation and [`docs/network-lab/experiment-results.md`](docs/network-lab/experiment-results.md) for baseline vs degraded results.

---

## Run Locally

```bash
# Install dependencies
pip install fastapi uvicorn requests prometheus-client pyyaml

# Start sample service (healthy baseline)
ARTIFICIAL_DELAY_MS=0 ERROR_MODE=false \
  python3 -m uvicorn sample_app.main:app --host 127.0.0.1 --port 9000 &

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
| Composite resilience score | ❌ | ✅ |
| Structured scorecards | ❌ | ✅ |
| Network-aware validation | ❌ | ✅ |
| Dependency-path diagnostics | ❌ | ✅ |
| Auto-remediation recommendations | ❌ | ✅ |
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
| Metrics | Prometheus (`prometheus-client`) |
| Visualization | Grafana-ready |
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
