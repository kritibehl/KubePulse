# Network Operations Pack

This pack maps KubePulse diagnostics to production network-operations workflows.

| Scenario | Severity | Symptom | Probable Root Cause | Operate Decision | Release Decision |
|---|---|---|---|---|---|
| dns_resolution_failure | high | service hostname does not resolve | DNS record missing, stale service discovery entry, or resolver issue | unsafe_to_operate | block |
| tcp_connection_timeout | high | TCP connection times out before application response | routing issue, firewall drop, overloaded listener, or unreachable host | unsafe_to_operate | block |
| blocked_port_iptables | medium | host reachable but expected service port is blocked | iptables/firewall/security-group rule blocks inbound traffic | unsafe_to_operate | hold |
| packet_loss_latency_spike | medium | HTTP succeeds but p95/p99 latency and packet loss exceed threshold | degraded route, congestion, packet loss, or dependency saturation | degraded | hold |
| service_unreachable_health_green | critical | application health remains green while dependency path is unreachable | health check does not validate downstream dependency reachability | unsafe_to_operate | block |

## Diagnostic Command Coverage

### dns_resolution_failure

Commands used:
- `dig service.internal`
- `nslookup service.internal`
- `cat /etc/resolv.conf`

Pre-change verification:
- confirm hostname fails resolution
- verify resolver configuration

Post-change verification:
- hostname resolves to expected IP
- HTTP health succeeds through resolved host

Recommended escalation: escalate to DNS/service-discovery owner if record is missing or resolver is degraded

### tcp_connection_timeout

Commands used:
- `nc -vz host 5000`
- `curl -v --connect-timeout 2 http://host:5000/health`
- `traceroute host`

Pre-change verification:
- TCP connect fails or times out
- route to host is unstable or blocked

Post-change verification:
- TCP connect succeeds
- HTTP health returns expected status

Recommended escalation: escalate to network/oncall owner if timeout persists across hosts

### blocked_port_iptables

Commands used:
- `sudo iptables -L -n`
- `ss -ltnp`
- `nc -vz host 5000`

Pre-change verification:
- process listens locally
- remote TCP check fails

Post-change verification:
- firewall rule allows expected port
- remote TCP check succeeds

Recommended escalation: escalate to host/network firewall owner if rule is managed centrally

### packet_loss_latency_spike

Commands used:
- `ping -c 20 host`
- `mtr host`
- `curl -w '%{time_total}\n' http://host/health`

Pre-change verification:
- packet loss or latency spike reproduced
- p95/p99 latency exceeds budget

Post-change verification:
- packet loss returns within threshold
- p95/p99 latency returns within budget

Recommended escalation: escalate to network reliability owner if loss is path-related

### service_unreachable_health_green

Commands used:
- `curl -v http://app/health`
- `nc -vz dependency 5432`
- `dig dependency.internal`

Pre-change verification:
- app health returns 200
- dependency TCP or DNS check fails

Post-change verification:
- dependency reachability restored
- readiness check includes dependency validation

Recommended escalation: escalate to service owner and dependency owner; block release until readiness reflects dependency state
