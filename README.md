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
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

*Validate recovery. Expose health-check blind spots. Ship with confidence.*

</div>

---

## The Problem

Production failures are often caused not by the disruption itself — but by **incorrect health signals masking degraded behavior**.

Traditional chaos engineering tools inject failures and stop there. They don't answer the questions that actually matter in production:

- Did the system **recover correctly**, or just appear to?
- Are your **readiness probes lying** to Kubernetes while requests fail?
- How long does recovery actually take **under real load**?

KubePulse answers these questions.

---

## What is KubePulse?

KubePulse is a **resilience validation framework** for Kubernetes services. It executes controlled disruption scenarios and measures whether systems recover correctly — producing structured, scorecarded reports that expose reliability blind spots before they impact production.

```
Disruption → Measurement → Validation → Scorecard → Report
```

KubePulse focuses on two things traditional fault injection tools miss:

1. **Recovery behavior** — Did the system return to a healthy state? How long did it take? How many restarts?
2. **Health signal correctness** — Are your probes reporting truthfully, or masking degraded states as healthy?

---

## Core Capabilities

### Declarative Scenario Execution

Disruption scenarios are defined declaratively and evaluated through a reusable validation pipeline. Each scenario produces a structured resilience report and scorecard.

| Scenario | Description |
|---|---|
| `cpu_pressure` | Simulates sustained CPU saturation and measures pod stability and recovery |
| `memory_pressure` | Applies memory stress and tracks restart behavior and probe integrity |
| `readiness_false_positive` | Detects cases where readiness probes report healthy during degraded service states |

---

### Resilience Scorecards

Every scenario run generates a scorecard evaluating observed system behavior under failure:

```json
{
  "scenario": "readiness_false_positive",
  "recovery_window_seconds": 42,
  "restart_count": 3,
  "readiness_probe_integrity": false,
  "latency_p95_ms": 650,
  "error_rate_percent": 8.0,
  "result": "fail",
  "recommendation": "Readiness probe does not reflect actual service health. Implement endpoint-level health checks that validate downstream dependencies."
}
```

Scorecard fields:

| Field | Description |
|---|---|
| `recovery_window` | Time from disruption to stable healthy state |
| `restart_count` | Pod restarts observed during the scenario |
| `readiness_probe_integrity` | Whether probes accurately reflected service health |
| `latency_p95` | 95th-percentile latency during degraded state |
| `error_rate` | Observed error rate during disruption |
| `result` | `pass` / `fail` |
| `recommendation` | Actionable mitigation guidance |

Reports are exported as **JSON resilience reports** and **Markdown resilience summaries**.

---

### Readiness Integrity Validation

KubePulse's most critical capability: detecting **readiness false positives** — cases where Kubernetes marks a pod as ready while the service is degraded.

```
Readiness before: ready
Readiness after:  ready          ← probe says healthy

Observed latency p95:  650 ms   ← service is not healthy
Observed error rate:   8%

Result:
  readiness_false_positive = true
  status                   = fail
```

This exposes the class of reliability blind spots that traditional fault injection tools and basic monitoring consistently miss. When probes lie, Kubernetes routes traffic to broken pods — and your dashboards show green.

---

### Observability Integration

KubePulse integrates with **Prometheus** and **Grafana** to visualize resilience signals and cluster behavior during scenario execution.

**Tracked metrics:**

| Metric | Description |
|---|---|
| `pods_running` | Active pod count during disruption |
| `cluster_errors` | Observed error count |
| `chaos_mode` | Disruption scenario active flag |

**Additional signals captured in resilience reports:**

- Recovery window timeline
- Restart activity patterns
- Probe mismatch detection
- Latency degradation curves
- Error rate over disruption window

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    KubePulse Framework                  │
│                                                         │
│  ┌──────────────┐    ┌───────────────────────────────┐  │
│  │  FastAPI     │    │     Scenario Runner            │  │
│  │  Execution   │───▶│  ┌─────────────────────────┐  │  │
│  │  API         │    │  │  YAML Scenario Definitions│  │  │
│  └──────────────┘    │  └─────────────────────────┘  │  │
│                      │  ┌─────────────────────────┐  │  │
│                      │  │  Resilience Evaluator    │  │  │
│                      │  └─────────────────────────┘  │  │
│                      │  ┌─────────────────────────┐  │  │
│                      │  │  Readiness Validator     │  │  │
│                      │  └─────────────────────────┘  │  │
│                      └───────────────────────────────┘  │
│                                    │                     │
│                    ┌───────────────┴──────────────┐      │
│                    ▼                              ▼      │
│           ┌──────────────┐             ┌──────────────┐  │
│           │  Scorecard   │             │    Report    │  │
│           │  Generation  │             │    Export    │  │
│           └──────────────┘             │  JSON │ .md  │  │
│                                        └──────────────┘  │
└─────────────────────────────────────────────────────────┘
              │                        │
    ┌─────────▼──────────┐   ┌────────▼────────┐
    │     Prometheus     │   │     Grafana      │
    │  (metrics export)  │   │  (visualization) │
    └────────────────────┘   └─────────────────┘
```

**Components:**

- **FastAPI scenario execution API** — HTTP interface for triggering and querying scenarios
- **YAML scenario definitions** — Declarative disruption scenario configuration
- **Scenario runner & resilience evaluator** — Executes scenarios and measures recovery behavior
- **Readiness integrity validator** — Detects probe-signal mismatches during degraded states
- **Resilience scorecard generation** — Structured pass/fail evaluation with recommendations
- **JSON and Markdown report export** — Portable resilience report artifacts

---

## Usage

### Run Locally

```bash
uvicorn app.main:app --reload
```

### API Reference

**Execute a validation scenario**
```bash
curl -X POST http://127.0.0.1:8000/scenarios/run/readiness_false_positive
```

**Retrieve the latest resilience scorecard**
```bash
curl http://127.0.0.1:8000/scorecard/latest
```

**Export a resilience report**
```bash
curl http://127.0.0.1:8000/reports/export/latest
```

**Available scenario endpoints:**

| Endpoint | Scenario |
|---|---|
| `POST /scenarios/run/cpu_pressure` | CPU saturation scenario |
| `POST /scenarios/run/memory_pressure` | Memory stress scenario |
| `POST /scenarios/run/readiness_false_positive` | Readiness integrity validation |
| `GET /scorecard/latest` | Retrieve latest scorecard |
| `GET /reports/export/latest` | Export latest report |

---

## Why KubePulse

> *"Your readiness probes are green. Your dashboards are green. Your users are getting errors."*

KubePulse validates both sides of the reliability equation:

| Traditional Chaos Tools | KubePulse |
|---|---|
| Injects failures | Injects failures **and measures recovery** |
| Reports that chaos happened | Reports **whether the system recovered correctly** |
| Ignores health signals | **Validates health-signal accuracy** |
| No actionable output | Generates **scorecards with mitigation guidance** |

Engineers use KubePulse to detect reliability blind spots — misconfigured probes, slow recovery paths, unstable restarts — before they cause production incidents.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.11+ |
| API | FastAPI |
| Orchestration | Kubernetes |
| Metrics | Prometheus |
| Visualization | Grafana |
| Report Formats | JSON, Markdown |

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