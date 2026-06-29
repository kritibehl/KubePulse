# Web Service Debugging Matrix

KubePulse explains contradictions between DNS, TCP, HTTP, latency, and dependency signals.

## Debugging Matrix

| Observation | Likely Failure Class | Interpretation | Suggested Next Check |
|---|---|---|---|
| DNS passes, TCP fails | port / firewall / bind issue | hostname resolves, but service is not reachable on expected port | check bind address, firewall/security group, listening process |
| TCP passes, HTTP fails | application / service issue | network path is open, but app health endpoint is failing | check app logs, route handler, dependency errors |
| HTTP 200 but latency high | performance degradation | endpoint responds, but user-visible latency violates budget | check p95/p99 latency, dependency saturation, retry amplification |
| Dependency fails | downstream integration issue | service may be healthy locally but unsafe due to dependency failure | check downstream DNS/TCP/HTTP and timeout behavior |

## Why This Matters

A service can look partially healthy at one layer while failing at another.

KubePulse separates:

- name resolution
- socket reachability
- HTTP service behavior
- latency / performance
- downstream dependency health

This helps classify production failures faster and avoids treating every outage as a generic service failure.

## Example

```json
{
  "case": "DNS passes, TCP fails",
  "likely_root_cause": "port/firewall/bind issue",
  "next_action": "verify service listens on 0.0.0.0:5000 and firewall allows inbound traffic"
}
