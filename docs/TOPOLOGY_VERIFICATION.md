# KubePulse Control-Plane/Data-Plane Verification

KubePulse is a rollout safety gate that compares Kubernetes control-plane intent with Cilium/Hubble-observed data-plane behavior.

## Problem

Kubernetes readiness tells us whether a pod is considered ready to receive traffic.

It does not prove that traffic is reaching the backend implied by deployment intent.

A rollout can therefore remain operational while the network data plane is degraded or while successfully forwarded traffic reaches an unexpected backend.

KubePulse evaluates both network regression and topology consistency before allowing an Argo Rollout to continue.

## Architecture

```text
Argo Rollout
    |
    v
AnalysisRun
    |
    v
KubePulse metric-provider plugin
    |
    +-------------------------------+
    |                               |
    v                               v
Cilium / Hubble Relay         Kubernetes API
observed network flows        Service
                              EndpointSlices
                              Pods
    |                               |
    +---------------+---------------+
                    |
                    v
          topology comparison
                    |
         PASS / FAIL / INCONCLUSIVE
                    |
                    v
       AnalysisRun / rollout decision
Live Network-Regression Proof

KubePulse reproduced a Kubernetes readiness false positive in a real kind, Cilium, Hubble, and Argo Rollouts environment.

Observed result:

stable readiness       2/2
canary readiness       1/1

stable flow events     2,219
canary flow events     106

stable observed
flow-event drop rate   0%

canary observed
flow-event drop rate   43.4%

KubePulse              FAIL
AnalysisRun            Failed
Rollout                Aborted
stable revision        preserved

These measurements are Hubble flow-event rates, not deduplicated request counts or packet-loss percentages.

Control-Plane Intent

KubePulse resolves the expected backend set using:

Service
   |
   v
EndpointSlices
   |
   v
eligible endpoints
   |
   v
Pod identity + IP

The resolver:

unions multiple EndpointSlices
excludes Ready=false endpoints
excludes Terminating=true endpoints
permits Ready=nil endpoints
resolves Pod identity and labels through TargetRef
supports IP-only endpoints
deduplicates and deterministically sorts results
Data-Plane Observation

KubePulse consumes Hubble protobuf flows and reconstructs directed source-to-destination edges while preserving:

source namespace, Pod, IP, and labels
destination namespace, Pod, IP, and labels
destination Service
Hubble verdict

Only FORWARDED edges establish realized reachability.

Dropped traffic does not prove that an unexpected destination was successfully reached.

Comparison Semantics

KubePulse produces:

PASS
FAIL
INCONCLUSIVE

Rules include:

no expected endpoints
    -> INCONCLUSIVE
       NO_EXPECTED_ENDPOINTS

no observed forwarded traffic
    -> INCONCLUSIVE
       NO_OBSERVED_FORWARDED_TRAFFIC

forwarded destination outside expected set
    -> FAIL
       CONTROL_DATA_PLANE_DIVERGENCE

all forwarded destinations inside expected set
    -> PASS

Pod identity is preferred when available.

Destination IP is used as a fallback when Hubble Pod identity is unavailable.

KubePulse does not require every eligible backend to appear during a finite observation window.

Semantic-Routing Harness

The checked-in topology experiment models:

CONTROL PLANE

payment-v2 Service
        |
        v
payment-v2 EndpointSlice
        |
        v
payment-v2 Pod

while the canary workload intentionally targets:

DATA PLANE

checkout-v2
        |
        v
payment-v1
FORWARDED

The topology comparison engine classifies this contradiction as:

CONTROL_DATA_PLANE_DIVERGENCE
decision = FAIL

The deterministic Argo plugin tests verify that this topology decision maps to a Failed analysis measurement.

The repository does not claim that this second topology scenario completed as a live end-to-end Argo abort experiment.

Validation

Topology comparator tests cover:

expected destination pass
partial observation of an expected backend set
unexpected destination failure
Pod identity precedence
IP fallback
dropped unexpected edge handling
missing expected endpoints
missing forwarded traffic
repeated-flow deduplication

Kubernetes resolver tests cover:

multiple EndpointSlices
Ready=false exclusion
terminating endpoint exclusion
IP-only endpoints
empty EndpointSlice result
missing Service failure

The Hubble collector is tested against an in-process gRPC/protobuf server.

The Argo plugin tests verify:

topology divergence -> Failed
topology pass -> existing network gate continues
missing expected endpoints -> Inconclusive
lost topology telemetry -> Inconclusive
invalid topology configuration -> validation error
Project Identity

KubePulse is not a generic Kubernetes monitoring dashboard.

It is a control-plane/data-plane verification system for progressive delivery.

Its core question is:

Can Kubernetes and a rollout controller report healthy deployment state while the actual network data plane is degraded or semantically inconsistent with intended routing?

KubePulse uses independent control-plane and data-plane evidence to answer that question before rollout promotion.
