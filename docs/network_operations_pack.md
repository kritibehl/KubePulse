# Network Operations Pack

KubePulse includes a Network Operations pack for production-style network troubleshooting and release safety.

## Scenario Coverage

- DNS resolution failure
- TCP connection timeout
- blocked port / iptables rule
- packet loss / latency spike
- service unreachable while app health remains green

## Output Fields

Each scenario captures:

- incident severity
- detected symptom
- probable root cause
- commands used for diagnosis
- pre-change verification
- post-change verification
- recommended escalation
- operate decision
- release decision

## Why This Matters

Network operations work requires separating symptoms across DNS, TCP, HTTP, routing, firewall, latency, and dependency layers. KubePulse generates incident-ready artifacts that map symptoms to root cause, remediation, escalation, and rollout decisions.

## Example

```json
{
  "scenario": "service_unreachable_health_green",
  "incident_severity": "critical",
  "detected_symptom": "application health remains green while dependency path is unreachable",
  "probable_root_cause": "health check does not validate downstream dependency reachability",
  "operate_decision": "unsafe_to_operate",
  "release_decision": "block"
}
