# Network Service Health

KubePulse evaluates network and application reachability across the full service path.

## Diagnostic Checklist

- DNS resolution
- TCP connectivity
- TLS handshake
- HTTP / HTTPS health
- proxy-style service reachability
- latency-budget validation
- dependency health
- operate/block decision
- incident escalation

## Proxy-Style Reachability Path

Example:

```text
client -> ingress/proxy -> application service -> PostgreSQL dependency
KubePulse does not claim Envoy, nginx, or HAProxy implementation experience. It validates the behavior expected around a proxy-style service path:

frontend hostname resolves
frontend TCP/TLS listener accepts connections
HTTP health route responds
upstream application remains healthy
downstream dependency remains reachable
end-to-end latency remains within budget
Layered Failure Interpretation
Result	Likely Issue
DNS fails	DNS/service-discovery failure
DNS passes, TCP fails	port, firewall, routing, or bind-address failure
TCP passes, TLS fails	certificate, protocol, or secure-listener failure
TLS passes, HTTP fails	application route or upstream service issue
HTTP 200, latency fails	performance degradation
app passes, dependency fails	downstream integration issue
Operate / Release Decision

Any critical failed layer produces:

{
  "operate_decision": "unsafe_to_operate",
  "release_decision": "block"
}
Escalation

Escalate based on the failed layer:

DNS/service discovery owner
network/firewall owner
TLS/certificate owner
application service owner
downstream dependency owner
