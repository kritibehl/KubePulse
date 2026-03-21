<div align="center">

```
██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗
██║ ██╔╝██║   ██║██╔══██╗██╔════╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝
█████╔╝ ██║   ██║██████╔╝█████╗  ██████╔╝██║   ██║██║     ███████╗█████╗
██╔═██╗ ██║   ██║██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝
██║  ██╗╚██████╔╝██████╔╝███████╗██║     ╚██████╔╝███████╗███████║███████╗
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝
```
# KubePulse

**Resilience validation for Kubernetes services — beyond "chaos ran" toward "did the system actually recover correctly?"**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.27+-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Prometheus](https://img.shields.io/badge/Prometheus-implemented-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-ready-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com)
[![CI](https://img.shields.io/badge/CI-passing-22C55E?style=flat-square&logo=githubactions&logoColor=white)](.github/workflows/resilience-tests.yml)
[![License](https://img.shields.io/badge/License-MIT-6366F1?style=flat-square)](LICENSE)

KubePulse is a resilience validation framework that executes controlled disruption scenarios, measures real service behavior, compares against a pre-disruption baseline, and produces structured scorecards — so engineers know whether their system recovered correctly, not just whether it survived.

---

## What This Looks Like in Practice

> Service stayed `Ready`. Kubernetes dashboard was green. Users were seeing elevated latency and errors.
>
> KubePulse ran a `readiness_false_positive` scenario, measured real request behavior against the pre-disruption baseline, and failed the run with `probe_truthfulness: misleading` and `resilience_score: 41`.

That gap — between what Kubernetes believes and what users experience — is what KubePulse is built to catch.

---

## The Problem

Traditional chaos tools inject failures and stop there. They don't answer the questions that actually matter:

| Question | What Most Tools Give You |
|---|---|
| Did the system recover correctly, or just appear to? | ❌ No baseline comparison |
| Are your readiness probes lying to Kubernetes? | ❌ Assumed trustworthy |
| How long does recovery take under real load? | ❌ No measurement |
| Is latency regressing after recovery? | ❌ No per-run history |

> *"Your readiness probes are green. Your dashboards are green. Your users are getting errors."*

KubePulse answers all of these.

---

## KubePulse vs. Traditional Chaos Tools

| Capability | Traditional Chaos | KubePulse |
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

---

## Core Workflow

```
Scenario YAML → Chaos Injector → Metrics Probe → Baseline Comparison
      → Readiness Validation → Resilience Score → Scorecard → Report
```

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                          KubePulse Platform                           │
│                                                                       │
│  FastAPI Control Plane ───▶ Validation Pipeline                       │
│                                                                       │
│                              Scenario Loader                          │
│                                    ↓                                  │
│                              Chaos Injector                           │
│                                    ↓                                  │
│                              Real Metrics Probe (p50/p95/p99)         │
│                                    ↓                                  │
│                              Baseline Comparison Engine               │
│                                    ↓                                  │
│                              Readiness Integrity Validator            │
│                                    ↓                                  │
│                              Resilience Score Engine                  │
│                                                                       │
│         Report Store (JSON)    Markdown Exports    Prometheus /metrics │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Scenario Catalog

Scenarios are declared as YAML in `scenarios/` and loaded dynamically — extensible without code changes.

```yaml
name: cpu_stress
type: cpu_stress
target:
  namespace: default
  pod_name: demo-pod
thresholds:
  recovery_window_seconds_max: 15
  restart_count_max: 1
  readiness_false_positive_allowed: false
```

| Scenario | What It Validates |
|---|---|
| `cpu_stress` | CPU starvation and thread contention |
| `cpu_pressure` | Sustained CPU saturation |
| `memory_pressure` | Heap pressure and OOM-adjacent behavior |
| `readiness_false_positive` | Probe-signal mismatch detection |
| `packet_loss` | Network instability and retry storms |
| `pod_kill` | Pod termination and rescheduling |
| `dependency_timeout` | Downstream dependency failure |

---

## Readiness Integrity Validation

KubePulse detects **readiness false positives** — cases where Kubernetes marks a pod `Ready` while the service is actually degraded.

```
Readiness before: ready
Readiness after:  ready          ← probe says healthy

Observed latency p95:  elevated
Observed error rate:   elevated  ← service is not healthy

Result:
  readiness_false_positive = true
  status                   = fail
```

---

## Resilience Scoring

Each run produces a composite score across four independent dimensions:

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

---

## Example Scorecards

**CPU stress — passing run:**

```json
{
  "scenario": "cpu_stress",
  "status": "pass",
  "recovery_window_seconds": 8,
  "restart_count": 0,
  "probe_mismatch": false,
  "latency_p95_ms": 210,
  "error_rate": 0.02,
  "resilience_score": 86
}
```

**Readiness false positive — failing run:**

```json
{
  "scenario": "readiness_false_positive",
  "status": "fail",
  "probe_mismatch": true,
  "readiness_before": "ready",
  "readiness_after": "ready",
  "readiness_false_positive": true,
  "recommendation": "Tighten readiness checks to better reflect degraded service state."
}
```

---

## Network-Aware Validation

KubePulse includes network disruption as first-class validation primitives: packet loss, DNS failure, latency injection, TCP resets, connection churn, and partition scenarios.

**Example — DNS Failure baseline vs. degraded:**

| Metric | Baseline | Degraded | Delta |
|---|---:|---:|---:|
| Network health score | 95 | 53 | −42 |
| DNS success rate | 98.5% | 55.0% | −43.5 pts |
| TCP connect latency | 18 ms | 145 ms | +127 ms |
| HTTP success rate | 99.0% | 72.0% | −27.0 pts |
| p95 latency | 165 ms | 315 ms | +150 ms |
| Recovery window | 5s | 14s | +9s |
| Readiness false positives | 0 | 2 | +2 |

---

## Observability

Prometheus-compatible scrape endpoint at `GET /metrics`:

| Metric | Description |
|---|---|
| `kubepulse_scenarios_total` | Total executions by result |
| `kubepulse_latency_ms` | Observed latency histogram per scenario |
| `kubepulse_error_events` | Error count per scenario |
| `pods_running` | Active pod count during disruption |
| `chaos_mode` | Boolean — disruption scenario active |

---

## CI Integration

Ships with a GitHub Actions workflow (`.github/workflows/resilience-tests.yml`) that runs resilience validation on every push and pull request. **Latest run: ✅ passing · ~15s**

---

## Quickstart

```bash
git clone https://github.com/kritibehl/KubePulse.git
cd KubePulse

pip install fastapi uvicorn requests prometheus-client pyyaml

# Start the injectable sample service
ARTIFICIAL_DELAY_MS=0 ERROR_MODE=false \
  python3 -m uvicorn sample_app.main:app --host 127.0.0.1 --port 9000 &

# Start KubePulse
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Run a scenario
curl -X POST http://127.0.0.1:8000/scenarios/run/readiness_false_positive

# Get latest scorecard
curl http://127.0.0.1:8000/scorecard/latest
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/scenarios` | List available scenarios |
| `POST` | `/scenarios/run/{name}` | Execute a named scenario |
| `GET` | `/scorecard/latest` | Latest resilience scorecard |
| `GET` | `/reports/export/latest` | Export latest report as Markdown |
| `GET` | `/metrics` | Prometheus endpoint |

---

## Repo Structure

```
app/              FastAPI control plane + validation pipeline
scenarios/        YAML scenario definitions
sample_app/       Fault-injectable test service
lab/network-lab/  Container-based network disruption lab
reports/          JSON experiment artifacts
exports/          Markdown resilience summaries
.github/          CI workflows
```

---

## Related Projects

- [Faultline](https://github.com/kritibehl/faultline) — correctness under failure for job execution
- [DetTrace](https://github.com/kritibehl/dettrace) — distributed incident replay and forensics
- [AutoOps-Insight](https://github.com/kritibehl/autoops-insight) — operator-facing incident triage
- [FairEval-Suite](https://github.com/kritibehl/FairEval-Suite) — regression gating for GenAI systems

## License

MIT — see [LICENSE](LICENSE) for details.
