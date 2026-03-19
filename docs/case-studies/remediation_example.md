# Remediation Recommendation Example

## Scenario
DNS failure between `frontend` and `auth-service`

## Observed Signals
- DNS success rate: 55.0%
- TCP connect latency: 145 ms
- HTTP success rate: 72.0%
- Network health score: 53
- Readiness false positives: true

## Recommendation Output
- probable source of degradation: cluster DNS resolution path
- recommended action: reroute
- confidence: 0.93
- suggested rollback: Rollback recent DNS policy or service-discovery changes.
- suggested config change: Validate CoreDNS, stub domains, and service discovery policy. Tighten readiness probes to reflect real dependency availability.

## Operator Interpretation
This recommendation indicates the system is likely suffering from service-discovery degradation rather than pure app-level instability. The right first response is not blind restart churn, but routing and DNS-policy validation.
