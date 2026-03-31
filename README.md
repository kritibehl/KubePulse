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

<<<<<<< HEAD
**Resilience validation for Kubernetes services — beyond "chaos ran" toward "did the system actually recover correctly?"**
=======
# KubePulse
>>>>>>> 9b6940c (Position KubePulse as resilience validation framework with network lab extensions)

**Kubernetes resilience validation framework measuring recovery, probe integrity, and degraded-path behavior under failure.**

<<<<<<< HEAD
KubePulse is a resilience validation framework that executes controlled disruption scenarios, measures real service behavior, compares against a pre-disruption baseline, and produces structured scorecards — so engineers know whether their system recovered correctly, not just whether it survived.

---

## What This Looks Like in Practice

> Service stayed `Ready`. Kubernetes dashboard was green. Users were seeing elevated latency and errors.
>
> KubePulse ran a `readiness_false_positive` scenario, measured real request behavior against the pre-disruption baseline, and failed the run with `probe_truthfulness: misleading` and `resilience_score: 41`.

That gap — between what Kubernetes believes and what users experience — is what KubePulse is built to catch.
=======
> KubePulse is not a chaos demo. It answers a harder operational question:
> **Did the service truly recover correctly, or did it only appear healthy?**
>>>>>>> 9b6940c (Position KubePulse as resilience validation framework with network lab extensions)

---

## The Problem

<<<<<<< HEAD
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
=======
Standard health checks lie.

A service can pass readiness probes, respond to HTTP pings, and show green in your dashboard — while still being unsafe to operate. Downstream DNS is broken. Latency has tripled. Dependency paths are degraded. Your probes don't know.

KubePulse measures whether systems are **actually safe to operate**, not just whether they are up.

---

## What KubePulse Validates

| Signal | What It Tells You |
>>>>>>> 9b6940c (Position KubePulse as resilience validation framework with network lab extensions)
|---|---|
| **Recovery time** | How long the system took to return to an acceptable state |
| **p50 / p95 latency drift** | Whether latency returned to baseline or remained degraded |
| **Probe integrity** | Whether readiness/health signals matched real availability |
| **DNS / dependency reachability** | Whether downstream services were actually reachable |
| **Error-rate change** | Whether degraded-path behavior increased failure rates |
| **Rollout risk** | Whether it was safe to continue deploying or restoring traffic |

---

<<<<<<< HEAD
## Readiness Integrity Validation

KubePulse detects **readiness false positives** — cases where Kubernetes marks a pod `Ready` while the service is actually degraded.
=======
## System States

| State | Recovery Time | Latency Drift | DNS Result | Readiness Integrity | Interpretation |
|---|---|---|---|---|---|
| **Healthy** | 0–5s | Minimal | Healthy | Probes aligned with real availability | Safe to operate |
| **Degraded** | Elevated / unstable | Significant drift | Partial or failed | False positives possible | May look healthy while still unsafe |
| **Recovered** | Returned to baseline | Drift normalizing | Path restored | Probes realigned | Safe to resume normal traffic |

---

## Network Lab

KubePulse includes a container-based service network lab for repeatable resilience experiments under controlled degradation.

### Dependency Path
>>>>>>> 9b6940c (Position KubePulse as resilience validation framework with network lab extensions)

```
edge -> api-service -> auth-service
```

<<<<<<< HEAD
---
=======
### Scenarios

- `baseline`
- `dns_failure`
- `latency_injection`
- `partial_partition`
- `connection_churn`
>>>>>>> 9b6940c (Position KubePulse as resilience validation framework with network lab extensions)

### Run in 5 Minutes

<<<<<<< HEAD
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
=======
> **Prerequisite:** Docker Desktop must be running.

```bash
docker compose -f lab/network-lab/docker-compose.yml up -d --build
bash lab/network-lab/scripts/run_experiment.sh baseline
bash lab/network-lab/scripts/run_experiment.sh dns_failure
```

Verify Docker is available:

```bash
docker info
>>>>>>> 9b6940c (Position KubePulse as resilience validation framework with network lab extensions)
```

---

## Network Lab Results

### DNS Failure

| | Baseline | Degraded |
|---|---|---|
<<<<<<< HEAD
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
=======
| Request success | 25 / 25 | **0 / 25** |

**Interpretation:** The dependency path was broken. The service was not safe to treat as recovered. Rollout and traffic restoration should be blocked until DNS resolution is restored.

### API Path Latency Injection

| | Baseline | Degraded |
|---|---|---|
| Request success | 25 / 25 | 23 / 25 |
| p50 latency | 4.888 ms | **1.462 s** |
| p95 latency | 10.120 ms | **2.306 s** |

**Interpretation:** The service path remained partially available, but degraded-hop behavior materially increased latency. The system may appear "up" — operator confidence should be reduced until the degraded path is resolved.

---

## Operational Questions KubePulse Answers

- Did recovery really complete?
- Are readiness probes still trustworthy?
- Is the service degraded even though it looks healthy?
- Is it safe to continue rollout, failover, or traffic restoration?
- Which signals suggest the biggest operational risk?

---

## Dependency-Path Diagnostics

KubePulse infers a lightweight dependency path and emits operator-facing signals:

- Upstream / downstream relationship hints
- Latency and error propagation path
- Likely root-cause service or network segment
- Estimated blast radius across impacted services

---
>>>>>>> 9b6940c (Position KubePulse as resilience validation framework with network lab extensions)

## Auto-Remediation Recommendations

<<<<<<< HEAD
MIT — see [LICENSE](LICENSE) for details.
=======
After each run, KubePulse emits a recommendation bundle:

- Probable source of degradation
- Recommended action: `restart` | `reroute` | `scale` | `isolate`
- Confidence score
- Suggested rollback
- Suggested config-change note

---

## Extending With a New Scenario

1. Add a failure script in `lab/network-lab/scripts/failures/`
2. Add the scenario branch in `lab/network-lab/scripts/run_experiment.sh`
3. Reuse the traffic and measurement scripts to capture:
   - Request success / failure
   - p50 / p95 latency
   - DNS / TCP behavior
   - Recovery timing
4. Document healthy vs degraded vs recovered outcomes
5. Add operator interpretation: safe to operate, still degraded, rollout risk, remediation recommendation

---

## Network-Aware Failure Primitives

KubePulse treats network disruption as first-class validation scenarios:

- Packet loss
- DNS resolution failure
- Service-to-service latency injection
- Node-to-node partition
- Dropped egress / degraded ingress
- MTU mismatch simulation
- Intermittent TCP resets
- Connection churn

For each run, KubePulse captures DNS success rate, TCP connect latency, HTTP success under degraded conditions, cross-zone communication degradation, path recovery time, and latency percentile drift relative to baseline.

---

## Productization Direction

KubePulse is structured as an operator-facing validation tool, not a one-off demo:

- Resilience validation scorecards
- Historical trend storage
- Repeated baseline vs degraded comparisons
- Network-aware failure scenarios
- Operator-facing reports with remediation guidance
- Fast scenario execution and extension workflows

---

## Artifacts

```
docs/scorecards/       # Resilience validation scorecards
docs/reports/          # Example run reports
docs/network-lab/      # Network lab result summaries
docs/screenshots/      # Service looked healthy / service was still degraded
```

---

## Core Idea

> A system can look healthy and still be unsafe to operate.

KubePulse exists to detect that gap — measuring whether systems recovered correctly, whether degraded-path behavior remains dangerous, and whether operators should trust what they are seeing.
>>>>>>> 9b6940c (Position KubePulse as resilience validation framework with network lab extensions)
