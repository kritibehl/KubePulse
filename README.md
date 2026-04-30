# KubePulse — Release Safety Validation for Distributed Systems

**KubePulse blocks unsafe releases when health checks lie.**

`Python` · `Kubernetes` · `FastAPI` · `Prometheus` · `Terraform (AWS EKS)` · `Docker`

---

**Latest proof:** AMD MI300X serving test blocked rollout after **+608% p95 latency regression** under long-prompt burst load — with the same pipeline that catches Kubernetes probe false positives.

---

## p95 Latency: Baseline vs Burst (AMD MI300X)

```
          p95 Latency (ms)
          │
  1422 ms │                              ████████████████████  BURST
          │                              █
          │                              █
          │                              █
          │                              █
          │                              █
          │                              █
   200 ms │  ███  BASELINE               █
          │
          └──────────────────────────────────────────────────
               Short prompts (4 req)     Long-prompt burst (24 req)

          Decision: BLOCK  (+608.34% regression, threshold exceeded)
```

---

## Run in 30 Seconds

```bash
git clone https://github.com/kritibehl/KubePulse
cd KubePulse
docker compose -f lab/network-lab/docker-compose.yml up -d --build
bash lab/network-lab/scripts/run_experiment.sh baseline
bash lab/network-lab/scripts/run_experiment.sh latency_injection
# → outputs safe_to_operate + release_decision per scenario
```

---

## Why This Project Matters in Hiring Terms

- Shows release safety engineering: detecting false-green health signals before they reach production
- Shows AI serving validation: the same pipeline works for Kubernetes microservices and GPU inference endpoints
- Shows reliability tooling design: composite resilience scoring, SLO tracking, error budget calculation
- Relevant to: SRE, platform engineering, AI infrastructure, release engineering

---

## Proof, Up Front

| Signal | Result |
|---|---|
| p95 latency drift detected | **+333%** — zero pod failures, probes green throughout |
| Decision generated | `block` |
| Error budget at decision point | **0.0%** |
| Readiness false positive confirmed | `probes_say_healthy: true` · `safe_to_operate: false` |
| DNS failure detection | 0/25 requests succeeded vs 25/25 baseline |
| API latency injection | p50: 4.9ms → 1,462ms · p95: 10.1ms → 2,306ms |
| AMD MI300X burst regression | **+608%** p95 (200ms → 1,422ms) → `block` |

---

## AMD MI300X — Serving Regression Caught

```
┌─────────────────────────────────────────────────────────┐
│  Platform:  AMD MI300X · vLLM 0.17.1 · ROCm            │
│  Model:     microsoft/Phi-3-mini-4k-instruct            │
│                                                         │
│  Baseline p95:   200.76 ms  (4 requests, short prompts) │
│  Burst p95:    1,422.07 ms  (24 requests, long prompts) │
│  Delta:          +608.34%                               │
│                                                         │
│  safe_to_operate:   false                               │
│  release_decision:  BLOCK                               │
│  reason:  p95 latency regression under long-prompt load │
└─────────────────────────────────────────────────────────┘
```

The same pipeline that catches Kubernetes probe false positives catches AI serving regressions. The decision contract is identical — `safe_to_operate` + `release_decision` — regardless of whether the system under test is a microservice or a GPU inference endpoint.

---

## The Problem

A service passes readiness checks. Dashboard is green. Traffic continues.

Meanwhile: downstream DNS is failing, a dependency cascade has tripled p95 latency, a topology reroute has put the service on a degraded path. **Readiness probes stayed green through all of it.**

Most deployment pipelines check container health. KubePulse checks user-visible health — and makes an explicit rollout decision when they diverge.

---

## The False-Green Problem, Demonstrated

Multi-service cascade (`edge → api → auth → postgres`). No pod restarts. No visible errors. Probes: green.

| Signal | Baseline | Degraded | Delta |
|---|---|---|---|
| p50 latency | 4.9 ms | 240 ms | +4,800% |
| p95 latency | 10.1 ms | 780 ms | **+333%** |
| p99 latency | — | 1,200 ms | +275% |
| Error rate | 0% | 8% | +8pp |
| Resilience score | 100 | **46** | −54 |
| Error budget remaining | — | **0.0%** | — |
| Probes healthy | `true` | **`true`** | ← misleading |
| Safe to operate | `true` | **`false`** | ← actual state |

```json
{
  "readiness_false_positive": true,
  "probes_say_healthy": true,
  "safe_to_operate": false,
  "release_decision": "block",
  "slo_violation": true,
  "error_budget_remaining": "0.0%"
}
```

**What the canonical decision looks like:**
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

## Architecture

```
YAML scenario definition
        │
        ▼
KubePulse scenario runner
        │
        ▼
Baseline capture (p50 / p95 / p99 / error rate)
        │
        ▼
Failure injection
  ├── CPU stress · pod kill · network partition
  ├── Latency injection · DNS failure
  └── AI service timeout · vector DB degradation
        │
        ▼
Degraded measurement + SLO evaluation
        │
        ▼
Probe integrity check
  └── probes_say_healthy  vs  safe_to_operate
        │
        ▼
Resilience score (composite, 0–100)
        │
        ▼
Decision artifact: continue / reroute / block
        │
        ▼
CI gate (GitHub Actions)
  └── blocks deployment if safe_to_operate=false
```

---

## Quick Demo

```bash
# Network lab — Docker only, no Kubernetes required
docker compose -f lab/network-lab/docker-compose.yml up -d --build
bash lab/network-lab/scripts/run_experiment.sh baseline
bash lab/network-lab/scripts/run_experiment.sh dns_failure
bash lab/network-lab/scripts/run_experiment.sh latency_injection
```

---

## Scenario Coverage

| Scenario | Failure type | Key signal |
|---|---|---|
| Readiness false positive | Topology failover + path reroute | `probes_say_healthy=true`, `safe_to_operate=false` |
| Multi-service cascade | DB latency → retry amplification | +333% p95 drift, `release_decision: block` |
| CPU stress | Pod CPU throttling | 8s recovery, resilience score 86/100 |
| DNS failure | Resolver failure | 0/25 success vs 25/25 baseline |
| API latency injection | Degraded hop | p50 4.9ms → 1,462ms |
| AI service timeout | Model inference spike | Fallback success rate, degraded-serving mode |
| Vector DB degradation | Retrieval latency | p99 drift, availability gap |

---

## Network Lab Results

**DNS failure:**

| | Baseline | Degraded |
|---|---|---|
| Request success | 25 / 25 | **0 / 25** |

**API latency injection:**

| | Baseline | Degraded |
|---|---|---|
| Requests succeeded | 25 / 25 | 23 / 25 |
| p50 latency | 4.888 ms | **1,462 ms** |
| p95 latency | 10.120 ms | **2,306 ms** |

---

## AMD MI300X Full Artifact

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

Artifacts: `amd_results/results/`

---

## CI Gate

```yaml
- name: Run KubePulse resilience gate
  run: python kubepulse/run_scenarios.py --gate
```

Every PR runs the full resilience suite. Deployments fail if resilience score drops below threshold or `safe_to_operate=false`.

---

## Full Setup — Kubernetes + Terraform

```bash
cd terraform/
terraform init
terraform apply
# Provisions: VPC · subnets · NAT gateway · EKS cluster · managed node group
```

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

## Why This Matters

The gap between "the pod is responding" and "the system is safe to route traffic to" is where real incidents happen: dependency latency spikes that cascade silently, retry storms that don't kill pods but do kill user experience, rollouts that succeed green and degrade traffic for 12 minutes before anyone notices.

Extending to GPU inference serving was a natural next step — the failure mode is the same (a system that appears available but is operationally unsafe), just on different hardware. The `safe_to_operate` + `release_decision` contract works identically across both.

---

## Limitations

- Simulation-based validation, not production traffic interception
- Network lab experiments run in Docker containers, not live Kubernetes clusters
- Latency and probe signals; not deep distributed tracing
- Terraform provisions a minimal EKS environment for test purposes
- GPU validation was run on AMD MI300X hardware; results are hardware-specific

---

## Interview Notes

**Design decision:** `safe_to_operate` as the exit interface. Everything the system measures feeds into one binary decision. That makes CI integration trivial and removes ambiguity ("the score is 72, is that okay?").

**Hard problem:** Distinguishing probe false positives from probe true positives requires both a baseline measurement and a degraded measurement — a single-point measurement doesn't tell you whether the current state is normal or degraded. Getting the baseline capture right (timing, warm-up, load pattern) is load-bearing.

**Tradeoff:** Simulation vs production traffic. Simulation gives repeatability and control; production traffic gives real failure modes. The current design prioritizes repeatability.

**What I'd build next:** Continuous drift detection — running the baseline comparison in production as a background process, catching gradual degradation between releases.

---

## Relevant To

`SRE` · `Platform Engineering` · `Backend / Infra` · `Release Engineering` · `AI Serving Infrastructure`

---

## Stack

Python · FastAPI · Kubernetes · Prometheus · Docker · Terraform (AWS EKS) · GitHub Actions

---

## Artifacts

```
docs/scorecards/       Resilience validation scorecards
docs/reports/          Run reports and what_probes_missed
docs/showcase/         Scenario matrix, false-green gallery, decision artifacts
docs/compare/          Baseline vs degraded vs recovered comparisons
amd_results/results/   AMD MI300X serving regression artifacts
```

---

## Related

- [Faultline](https://github.com/kritibehl/faultline) — exactly-once execution correctness under distributed failure
- [DetTrace](https://github.com/kritibehl/dettrace) — deterministic replay for concurrency failures
- [AutoOps-Insight](https://github.com/kritibehl/AutoOps-Insight) — CI failure intelligence and operator triage
- [FairEval-Suite](https://github.com/kritibehl/FairEval-Suite) — AI release gating and regression detection

## Validation Data Pipeline

KubePulse exports reproducible validation artifacts for network and rollout-safety scenarios.

Artifacts:

- `labs/network_reliability/dns_failure_report.json`
- `labs/network_reliability/degraded_path_report.json`
- `labs/network_reliability/latency_injection_report.json`

Export pipeline:

```bash
python pipelines/export_validation_runs.py

Output:

reports/validation_runs/validation_run_table.json

The validation table captures:

scenario results
p95 / p99 latency drift
error-rate deltas
degraded-path evidence
recovery windows
rollout decisions

This turns scenario runs into reusable validation data for CI/CD, SRE review, and platform release gates.
