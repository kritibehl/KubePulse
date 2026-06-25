# Network Reachability Diagnostics

KubePulse diagnoses service failures across DNS, TCP, HTTP, latency, host binding, and dependency reachability layers.

## Failure Classes

| Failure | Detection |
|---|---|
| DNS failure | hostname does not resolve |
| TCP port closed | socket connection fails |
| HTTP health failure | health endpoint fails |
| latency degradation | latency exceeds threshold |
| host binding failure | service reachable only on localhost / wrong bind address |
| dependency unreachable | downstream dependency cannot be reached |

## Example Incident

```json
{
  "incident": "Service unreachable",
  "root_cause": "Host binding failure or closed port",
  "evidence": [
    "DNS resolution: PASS",
    "TCP port 5000: FAIL",
    "HTTP health: FAIL"
  ],
  "suggested_remediation": [
    "bind service to 0.0.0.0 instead of localhost",
    "verify firewall or security group rules",
    "confirm process is listening on expected port",
    "restart service after config fix"
  ]
}
Done Criteria

KubePulse can diagnose whether a service failure is DNS-level, TCP-level, HTTP-level, latency-related, host-binding-related, or dependency-related, and generates a production-style report with evidence, root cause, and remediation.
