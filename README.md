# KubePulse

**Detects dangerous releases that pass readiness probes but are unsafe for users.**

5 scenarios · 0 false-safe decisions.

`Python` · `Kubernetes` · `FastAPI` · `Prometheus` · `Docker Compose` · `FRRouting`

---

## Why This Exists

**Problem:** Kubernetes readiness probes check whether a container is alive. They do not check whether the deployment is safe for users. A service can pass every probe while DNS is failing, p95 latency has tripled, and the error budget is at zero.

**Impact:** False-green deployments roll out. The problem compounds across deployment waves. Customers are impacted before anyone notices.

**Proof:** KubePulse compares probe state against user-visible health across four validation layers, and blocked 5 dangerous deployments in controlled testing — including a cascade where probes stayed green through +333% p95 latency and 8% error rate. 0 false-safe decisions.

---

## Latest Project Output

```json
{
  "release_decision": "BLOCK",
  "probes_say_healthy": true,
  "safe_to_operate": false,
  "p95_latency_impact": "+333%",
  "error_rate_increase": "+8%",
  "error_budget_remaining": "0.0%",
  "rollback_recommended": true
}
```

## Live Metrics Snapshot

| Signal | Value |
|---|---|
| Release Decision | **BLOCK** |
| Recovery Time | **12s** |
| P95 Latency Impact | **+333%** |
| Error Rate Increase | **+8%** |

---

## Latest Release Safety Report

| Scenario | Probe State | Safe to Operate | Decision |
|---|---|---|---|
| Readiness false positive | `PASS` | `false` | **BLOCK** |
| DNS failure | `PASS` | `false` | **BLOCK** |
| API latency injection (+22,831% p95) | `PASS` | `false` | **BLOCK** |
| Multi-service cascade (+333% p95) | `PASS` | `false` | **BLOCK** |
| Hardware release-gate test — AMD MI300X (+608% p95) | `PASS` | `false` | **BLOCK** |

---

## Why KubePulse

```
Deployment rolls out. All readiness probes: PASS.

Behind the scenes:
  edge-service → api-service → auth-service → postgres
  auth-service connection pool exhausted under load
  Cascade: api-service timeout → edge-service retry storm

KubePulse Layer 1:  p95 latency +7,623% · error rate 8%
Layer 3:            error_budget_remaining: 0.0%
Layer 4:            probes_say_healthy: true · safe_to_operate: false

Release decision: BLOCK · rollback_recommended: true
```

## Architecture

```
Deployment Trigger
      │
      ▼
Layer 1: Health Signals        p50 · p95 · p99 · error rate
      │
      ▼
Layer 2: Network Validation    DNS · TCP · TLS · auth
      │
      ▼
Layer 3: SLO Evaluation        error budget · resilience score
      │
      ▼
Layer 4: Probe Integrity       probes_say_healthy  vs  safe_to_operate
      │
      ├── divergence detected → release_decision: BLOCK + rollback recommendation
      └── all pass           → release_decision: continue
```

---

## Network Resilience Labs

Underneath the Kubernetes-facing gate is a validated networking layer:

- **eBGP resilience** — two-AS topology built with FRRouting and Linux network namespaces, explicit import/export prefix policies, routes traced from the BGP RIB into the Linux kernel FIB, TCP/179 withdrawal captures. Across 10 fault-injection runs: **251ms median / 270ms p95** end-to-end data-plane recovery (including host-side command and polling overhead).
- **LAN switching & VLANs** — VLAN-aware Linux bridges (VLAN 10/20, 802.1Q trunk), validated dynamic MAC/FDB learning and broadcast-domain isolation.
- **Inter-VLAN routing** — router-on-a-stick via 802.1Q subinterfaces, verified bidirectional L3 forwarding with correct TTL decrement.
- **Fault isolation & rollback** — deliberately broke VLAN 10 on one trunk endpoint: 100% loss isolated to VLAN 10 while VLAN 20 and the physical trunk stayed healthy. Diagnosed via VLAN forwarding state + packet capture, then restored and verified.

*These are controlled lab validations, not claims of production BGP or enterprise switch administration.*

---

## Control-Plane / Data-Plane Rollout Verification

A separate module answers a harder question than ordinary readiness monitoring: **can Kubernetes report a rollout as healthy while the observed network data plane is degraded or inconsistent with control-plane intent?**

Built with Argo Rollouts, Cilium/eBPF, Hubble Relay, and the Kubernetes Service/EndpointSlice APIs. A real canary stayed **1/1 Ready** while Hubble observed flow-event drop rate regress from 0% to **43.4%** across 2,219 stable and 106 canary flow events. KubePulse returned `FAIL`, the Argo `AnalysisRun` transitioned to `Failed`, and the rollout was auto-aborted while the healthy stable ReplicaSet stayed available.

The topology engine resolves intended destinations from `Service`/`EndpointSlice`, reconstructs source-to-destination topology from Hubble flows, and emits `CONTROL_DATA_PLANE_DIVERGENCE` when observed traffic reaches an unexpected backend — with explicit `PASS`/`FAIL`/`INCONCLUSIVE` semantics for insufficient evidence. See `docs/TOPOLOGY_VERIFICATION.md`.

A companion lab validated this with real Cilium v1.20.0 + Hubble Relay on a Kind cluster (arm64): 20/20 HTTP requests succeeded end-to-end while Hubble captured 200 namespace flow records.

---

## Operational Artifacts

KubePulse converts validation results into rollout gates, alerts, and incident reports:

- `ci_release_gate/` — CI/CD release gate demo
- `monitoring_alerting/` — alert policy + service health dashboard
- `incident_replays/` — recorded incident scenarios with evidence
- `slo/` — error-budget policy, burn-rate alerts, SLO reporting

Example SLO output:
```json
{ "availability": 99.92, "error_budget_remaining": 63, "release_decision": "block" }
```

---

## Repository Structure

```
KubePulse/
├── gate/              4-layer release-safety gate
├── lab/network-lab/   eBGP + VLAN network resilience labs
├── labs/
│   ├── ai_server_platform_validation/   Hardware-adjacent release-gate validation
│   └── network_reliability/              Degraded path / DNS failure / latency injection
├── scenarios/          YAML scenario definitions
├── diagnostics/         DNS · TCP · TLS · auth validation
├── ci_release_gate/      CI/CD release gate demo
├── monitoring_alerting/   Alerts + dashboards
├── incident_replays/       Recorded incidents with evidence
├── slo/                     Error-budget policy + SLO reporting
├── terraform/                 EKS/infra provisioning
├── docs/
└── reports/                     Gate decisions (CI-generated)
```

---

## Run Locally

```bash
git clone https://github.com/kritibehl/KubePulse && cd KubePulse
docker compose -f lab/network-lab/docker-compose.yml up -d --build
make demo    # all 5 scenarios
make test    # 0 false-safe decisions
make report  # → reports/latest/quality_soak_report.json
```

## Tests

```bash
make test
# ✓ readiness false positive     — probes=true · safe=false → BLOCK
# ✓ DNS failure                  — 0/25 requests succeed → BLOCK
# ✓ API latency injection        — p95 +22,831% → BLOCK
# ✓ multi-service cascade        — resilience score 100→46 → BLOCK
# ✓ AMD MI300X hardware release-gate test — p95 +608% → BLOCK
# 5 scenarios · 0 false-safe decisions
```

## About

Kubernetes resilience validation for real recovery behavior, probe integrity and rollout scorecards.
