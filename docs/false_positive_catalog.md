# KubePulse — Readiness False Positive Catalog

## Core Insight
Standard Kubernetes readiness probes can report "healthy" even when user-facing behavior is degraded.

KubePulse detects these mismatches using topology-aware failure modeling.

---

## 1. CPU-Throttled Recovery False Positive

**Scenario**
- Service under CPU stress
- Readiness probe still returns 200 OK

**Observed Behavior**
- Latency spikes (p95 > threshold)
- Increased error rate

**Probe Signal**
- Healthy

**KubePulse Detection**
- readiness_false_positive = true
- safe_to_operate = false

---

## 2. Link Failure Failover False Positive

**Scenario**
- Primary path fails
- Traffic rerouted to degraded path

**Observed Behavior**
- Increased latency
- Higher tail latency (p99)

**Probe Signal**
- Healthy

**What Probes Missed**
- Path degradation
- Latency inflation

---

## 3. Blackhole (Dependency Collapse)

**Scenario**
- Downstream dependency unreachable

**Observed Behavior**
- Requests fail
- Availability drops

**Probe Signal**
- May still show healthy upstream

**KubePulse Detection**
- Detects unreachable dependency path
- Blocks rollout

---

## 4. Asymmetric Path Latency Drift

**Scenario**
- Routing shifts to slower path

**Observed Behavior**
- Requests succeed but slower

**Probe Signal**
- Healthy

**KubePulse Detection**
- Latency drift
- Degraded path classification

---

## 5. Link Flap Instability

**Scenario**
- Repeated link up/down

**Observed Behavior**
- Intermittent latency spikes
- Request instability

**Probe Signal**
- Healthy

**KubePulse Detection**
- Path churn detection
- Instability classification

---

## Conclusion

Readiness probes answer:
> "Is the service alive?"

KubePulse answers:
> "Is the system safe to operate under real conditions?"
