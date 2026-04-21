<div align="center">

# KubePulse — Release Safety Validation for Distributed Systems

**Kubernetes tells you if your system is alive.**
**KubePulse tells you if it is safe to deploy.**

Detected **+333% p95 latency drift** with no pod failures and blocked rollout.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Scenarios-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Terraform](https://img.shields.io/badge/Terraform-AWS%20EKS-7B42BC?style=flat-square&logo=terraform&logoColor=white)](https://terraform.io)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)

</div>

---

## Decision Output

```json
{
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "latency drift + dependency cascade"
}
```

---

## False Green: The Core Problem

A service passes readiness checks. Dashboard is green. Traffic continues.

Meanwhile: downstream DNS is failing, dependency cascade has tripled p95 latency, a topology reroute put the service on a degraded path. **Readiness probes stayed green through all of it.**

KubePulse detects the gap between *container-level health* and *user-visible health* — and makes an explicit rollout decision.

---

## Scorecard: Multi-Service Cascade

Dependency chain modeled: `edge → api → auth → postgres`
No pod restarts. No visible errors. Probes: green.

| Signal | Baseline | Degraded | Delta |
|---|---|---|---|
| p50 latency | 4.9 ms | 240 ms | +4,800% |
| p95 latency | 10.1 ms | 780 ms | **+333%** |
| p99 latency | — | 1,200 ms | **+275%** |
| Error rate | 0% | 8% | +8pp |
| Resilience score | 100 | **46** | −54 |
| Error budget remaining | — | **0.0%** | — |
| Probes healthy | true | **true** | ← misleading |
| Safe to operate | true | **false** | ← actual state |

```json
{
  "readiness_false_positive": true,
  "probes_say_healthy": true,
  "safe_to_operate": false,
  "recommendation_action": "block",
  "slo_violation": true,
  "error_budget_remaining": "0.0%"
}
```

---

## Topology Failover: False Positive Demonstrated

A link failure triggers a reroute. Kubernetes reports healthy. The system is on a degraded alternate path.

```json
{
  "readiness_false_positive": true,
  "probes_say_healthy": true,
  "safe_to_operate": false,
  "recommendation_action": "reroute",
  "what_probes_missed": "degraded alternate path — higher latency, weaker margins"
}
```

---

## Network Lab Results

Container-based network lab for repeatable degradation experiments.

### DNS Failure

| | Baseline | Degraded |
|---|---|---|
| Request success | 25 / 25 | **0 / 25** |

The dependency path broke entirely. Readiness probes were not informed.

### API Path Latency Injection

| | Baseline | Degraded |
|---|---|---|
| Requests succeeded | 25 / 25 | 23 / 25 |
| p50 latency | 4.888 ms | **1,462 ms** |
| p95 latency | 10.120 ms | **2,306 ms** |

The service appeared "up." The latency made it operationally unsafe.

---

## What KubePulse Validates

| Signal | What it tells you |
|---|---|
| Recovery time | Did the system return to acceptable state, or just stop crashing? |
| p50 / p95 / p99 latency drift | Did latency return to baseline or stay elevated? |
| Probe integrity | Did readiness signals match real availability? |
| DNS / dependency reachability | Were downstream services actually reachable? |
| Error-rate delta | Did degraded-path behavior increase failure rates? |
| SLO pass/fail | Did behavior cross user-facing thresholds? |
| Error budget remaining | How much runway remains before SLO breach? |
| Rollout risk | Should traffic continue, reroute, or stop? |

---

## System States

| State | Recovery | Latency drift | Probes | Interpretation |
|---|---|---|---|---|
| Healthy | 0–5s | Minimal | Aligned | Safe to operate |
| Degraded | Elevated | Significant | **False positive possible** | Looks healthy, unsafe |
| Recovered | Baseline | Normalizing | Realigned | Safe to resume |

---

## Canonical Decision Artifact

```
┌─────────────────────────────────────────────────────────┐
│  Scenario: multi_service_cascade                        │
│                                                         │
│  Probes healthy?      YES  (misleading)                 │
│  SLO met?             NO                                │
│  Safe to operate?     NO                                │
│  Error budget left?   0.0%                              │
│                                                         │
│  What probes missed:  8% error rate, 333% p95 drift,   │
│                       9% availability gap               │
│                                                         │
│  Recommendation:      BLOCK rollout                     │
└─────────────────────────────────────────────────────────┘
```

---

## Visual Decision Artifact

![Topology Decision Artifact](docs/showcase/topology_decision_artifact.svg)

---

## Scenario Coverage

| Scenario | Failure type | Key signal |
|---|---|---|
| Readiness false positive | Topology failover + path reroute | `probes_say_healthy=true`, `safe_to_operate=false` |
| Multi-service cascade | DB latency → retry amplification | +333% p95 drift, `recommendation: block` |
| CPU stress | Pod CPU throttling | 8s recovery, resilience score 86/100 |
| DNS failure | Resolver failure | 0/25 success vs 25/25 baseline |
| API latency injection | Degraded hop | p50 4.9ms → 1,462ms |
| AI service timeout | Model inference spike | Fallback success rate, degraded-serving mode |
| Vector DB degradation | Retrieval latency | p99 drift, availability gap |

---

## AI Service Reliability

KubePulse includes scenario packs for Kubernetes-hosted AI services:

- Model inference timeout spikes
- Vector DB degraded latency
- Embedding service unavailable
- Tool-router dependency failure
- Partial fallback behavior under load

Scorecards surface: availability, p99 latency, fallback success rate, degraded-but-serving vs full outage. The condition "latency SLO passed but error budget exhausted" is expressible and detectable.

---

## Architecture

```
YAML scenario definition
        ↓
KubePulse scenario runner
        ↓
Baseline capture (p50 / p95 / p99 / error rate)
        ↓
Failure injection (CPU stress / pod kill / network partition / latency / DNS)
        ↓
Degraded measurement + SLO evaluation
        ↓
Probe integrity check
        ↓
Resilience score (composite)
        ↓
Decision artifact: continue / reroute / block
        ↓
CI gate (GitHub Actions) — blocks deployment if safe_to_operate=false
```

---

## Quickstart (Network Lab)

```bash
# Prerequisite: Docker Desktop running
docker compose -f lab/network-lab/docker-compose.yml up -d --build

bash lab/network-lab/scripts/run_experiment.sh baseline
bash lab/network-lab/scripts/run_experiment.sh dns_failure
bash lab/network-lab/scripts/run_experiment.sh latency_injection
```

---

## Infrastructure (Terraform / AWS EKS)

```bash
cd terraform/
terraform init
terraform apply
```

Provisions: VPC · public and private subnets · NAT gateway · EKS cluster · managed node group

---

## CI Gate

Every PR runs the full resilience suite. Deployments fail if resilience score drops below threshold or `safe_to_operate=false`.

```yaml
- name: Run KubePulse resilience gate
  run: python kubepulse/run_scenarios.py --gate
```

---
## AMD MI300X — AI Serving Validation

KubePulse extended to real GPU inference serving: ROCm + vLLM stack on AMD MI300X hardware, same baseline-vs-burst comparison pipeline, same block/continue decision output.

**Baseline (4 requests, short prompts)**

| Signal | Value |
|---|---|
| p95 latency | 200.76 ms |
| safe_to_operate | `true` |
| release_decision | `continue` |

**Long-prompt burst (24 requests)**

| Signal | Baseline | Burst | Delta |
|---|---|---|---|
| p95 latency | 200.76 ms | **1422.07 ms** | **+608.34%** |
| safe_to_operate | `true` | **`false`** | — |
| release_decision | `continue` | **`block`** | — |

```json
{
  "platform": "amd_mi300x",
  "model": "microsoft/Phi-3-mini-4k-instruct",
  "runtime": "vLLM 0.17.1 + ROCm",
  "baseline_p95_ms": 200.76,
  "candidate_p95_ms": 1422.07,
  "latency_p95_delta_pct": 608.34,
  "safe_to_operate": false,
  "release_decision": "block",
  "reason": "p95 latency regression under long-prompt burst load"
}
```

The same pipeline that catches Kubernetes probe false positives also catches AI serving regressions — whether the system under test is a distributed microservice or a GPU inference endpoint. The decision contract is identical.

Artifacts: [`amd_results/results/`](amd_results/results/)

## Why This Matters in Production

KubePulse started as a resilience validation tool. The core insight driving it is that container health and user-visible health are different measurements — and most deployment pipelines only check one of them. The gap between "the pod is responding" and "the system is safe to route traffic to" is where real incidents happen: dependency latency spikes that cascade silently, retry storms that don't kill pods but do kill user experience, rollouts that succeed green and degrade traffic for 12 minutes before anyone notices.

The false-green detection pattern maps directly to release-gating workflows at SRE and platform teams at FAANG scale.

---

## Scope and Limitations

- Simulation-based validation, not production traffic interception
- Network lab experiments run in Docker containers, not live Kubernetes clusters
- Latency and probe signals, not deep distributed tracing
- Terraform module provisions a minimal EKS environment for test purposes

---

## Artifacts

```
docs/scorecards/          Resilience validation scorecards
docs/reports/             Example run reports and what_probes_missed
docs/showcase/            Scenario matrix, false-green gallery, decision artifacts
docs/compare/             Baseline vs degraded vs recovered comparisons
```

---

## Signals For

`SRE` · `Platform Engineering` · `Backend / Infra` · `Release Engineering` · `Apple Validation / Tools` · `Google Production Systems` · `Microsoft Experimentation`

---

## Stack

Python · FastAPI · Kubernetes · Prometheus · Docker · Terraform (AWS EKS) · GitHub Actions

---

## Related

- [Faultline](https://github.com/kritibehl/faultline) — exactly-once execution correctness under distributed failure
- [DetTrace](https://github.com/kritibehl/dettrace) — deterministic replay for concurrency failures
- [AutoOps-Insight](https://github.com/kritibehl/AutoOps-Insight) — CI failure intelligence and operator triage
- [FairEval-Suite](https://github.com/kritibehl/FairEval-Suite) — AI release gating and regression detection
