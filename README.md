# KubePulse

**KubePulse detects false-green Kubernetes deployments — probes say healthy, users see failures.**

5 soak-test scenarios. 0 false-safe decisions. +608% regression blocked.

`Python` · `Kubernetes` · `FastAPI` · `Prometheus` · `Docker Compose`

---

## Proof

| Signal | Result |
|---|---|
| AMD MI300X burst p95 regression blocked | **+608%** → `BLOCK` |
| Multi-service cascade p95 drift | **+333%** · probes green throughout |
| Error budget at detection | **0.0%** |
| DNS failure detection | 0/25 requests vs 25/25 baseline |
| False-safe decisions across 5 scenarios | **0** |

---

## Screenshots

| Quality / Soak-Test Report | Network Diagnostic |
|---|---|
| ![Quality Report](reports/quality_soak_report.png) | ![Network](reports/network_diagnostic_report.png) |

> **To add:** `docs/gifs/false_green_demo.gif` — record `make demo` showing probes=green alongside safe_to_operate=false then BLOCK decision. Highest-ROI visual missing from this repo.

**False-green detection — what the report shows:**

```
┌──────────────────────────────────────────────────────────────┐
│  KubePulse Release Report                                     │
├────────────────────┬───────────────┬─────────────────────────┤
│  Signal            │  Probe layer  │  KubePulse              │
├────────────────────┼───────────────┼─────────────────────────┤
│  Container alive   │  ✓ PASS       │  ✓ PASS                 │
│  /healthz 200      │  ✓ PASS       │  ✓ PASS                 │
│  p95 latency       │  (not checked)│  780ms  +333%  ✗ FAIL   │
│  Error rate        │  (not checked)│  8%            ✗ FAIL   │
│  Error budget      │  (not checked)│  0.0% remaining ✗ FAIL  │
├────────────────────┴───────────────┴─────────────────────────┤
│  probes_say_healthy: true    safe_to_operate: false           │
│  release_decision: BLOCK                                      │
│  what_probes_missed: "333% p95 drift · 8% error rate"        │
└──────────────────────────────────────────────────────────────┘
```

---

## Problem

KubePulse is a release-safety platform. Everything else — DNS diagnostics, network validation, GPU serving tests — supports that goal.

Kubernetes readiness probes answer: *is this container alive?* They don't answer: *is this deployment safe for users?*

A service can pass every probe while:
- Downstream DNS is failing — 0 of 25 dependency requests succeed
- p95 latency has tripled — a topology reroute added 700ms to every request
- Error budget is gone — 8% error rate consumed the remainder
- A GPU serving endpoint is collapsing under burst load

**Probe state and user-visible health can diverge.** Rolling out in that state amplifies the problem.

---

## Why Existing Approaches Fail

**Probe-only pipelines:** Check container liveness. Don't measure downstream health, latency SLOs, or error budget. The false-green zone is everything probes don't measure.

**Reactive monitoring:** Catches problems after rollout completes. Doesn't block the rollout. Incident response starts after impact begins.

**Synthetic health checks:** Test specific endpoints on a schedule. Don't measure the full serving path under real traffic, dependency failures, or burst load.

---

## Decision Contract

```json
{
  "probes_say_healthy": true,
  "safe_to_operate": false,
  "release_decision": "block",
  "error_budget_remaining": "0.0%",
  "what_probes_missed": "333% p95 drift · 8% error rate · 9% availability gap",
  "rollback_recommended": true
}
```

---

## Architecture

![KubePulse Architecture](docs/architecture.png)

```
Deployment trigger
      │
      ▼
Layer 1: Health signals
  p50 / p95 / p99  ·  error rate  ·  throughput
      │
      ▼
Layer 2: Network / dependency validation
  DNS · TCP · TLS · downstream latency · auth endpoint
      │
      ▼
Layer 3: SLO / error budget evaluation
  budget remaining  ·  resilience score (0–100)
      │
      ▼
Layer 4: Probe integrity check
  probes_say_healthy  vs  safe_to_operate
  divergence → false-green detected
      │
      ▼
release_decision: continue / reroute / BLOCK
+ rollback recommendation + what_probes_missed
```

---

## Validation

| Scenario | Failure | Key signal | Decision |
|---|---|---|---|
| Readiness false positive | Topology reroute | probes=true · safe=false | **BLOCK** |
| DNS failure | Resolution failure | 0/25 requests | **BLOCK** |
| API latency injection | Downstream degradation | p95 +22,831% | **BLOCK** |
| Multi-service cascade | edge→api→auth→postgres | resilience 100→46 | **BLOCK** |
| AMD MI300X burst | Long-prompt GPU load | p95 +608% | **BLOCK** |

```bash
make test   # → 5 scenarios · 0 false-safe decisions
```

---

## Results

- **0** false-safe decisions across all 5 scenarios
- **+608%** p95 regression blocked on AMD MI300X — probes were not applicable
- **+333%** p95 drift blocked in multi-service cascade — probes green throughout
- Error budget at detection: **0.0%** remaining

---

## Tradeoffs

**Simulated failure injection, not production traffic.** Scenarios model realistic failure classes. Production would combine synthetic injection with real traffic sampling to catch patterns synthetic injection misses.

**Composite resilience score is a heuristic.** The 0–100 score weights latency, error rate, and availability. Weights are configurable but not formally derived from an SLO model. A production SLO compliance system would be more rigorous.

**Terraform / AWS EKS manifests are deployment artifacts.** They are proof of infrastructure design, not a managed production cluster.

---

## What This Project Does Not Claim

- Failure injection is simulated — not production traffic replay
- AMD MI300X results are from a controlled burst test — not sustained production load
- Terraform / EKS manifests are artifacts — not a managed production cluster
- Resilience score is a heuristic — not a formal SLO compliance system

---

## Quick Start

```bash
git clone https://github.com/kritibehl/KubePulse && cd KubePulse
docker compose -f lab/network-lab/docker-compose.yml up -d --build
make demo    # all 5 scenarios
make test    # 0 false-safe decisions
make report  # → reports/latest/quality_soak_report.json
```

---

## Further Reading

- [`docs/case_study.md`](docs/case_study.md) — Problem · Design · Validation · Tradeoffs
- [`docs/interview_walkthrough.md`](docs/interview_walkthrough.md) — 60s · 3min explanations

## Repository Map

```
KubePulse/
├── lab/network-lab/  Docker Compose scenarios + scripts
├── scenarios/        YAML scenario definitions
├── gate/             4-layer release-quality gate
├── diagnostics/      DNS · TCP · TLS · auth validation
├── docs/             Architecture · screenshots · case study
└── reports/          Soak-test + quality gate outputs
```
