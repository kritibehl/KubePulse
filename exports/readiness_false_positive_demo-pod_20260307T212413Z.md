# KubePulse Resilience Report

## Scenario
- **Scenario:** readiness_false_positive
- **Started At:** 2026-03-07T21:24:13.556016+00:00
- **Status:** fail

## Scorecard
- **Recovery Window (s):** 12.0
- **Restart Count:** 0
- **Probe Mismatch:** True
- **Readiness False Positive:** True

## Readiness Signals
- **Readiness Before:** ready
- **Readiness After:** ready

## Validation
- **Reason:** Readiness false positive detected while scenario disallowed it.
- **Recommendation:** Tighten readiness checks to better reflect degraded service state.

## Execution Output
### stdout

    Dry run: readiness remained healthy while service behavior degraded

### stderr

    

## Artifact
- **Source Report:** reports/readiness_false_positive_demo-pod_20260307T212413Z.json
