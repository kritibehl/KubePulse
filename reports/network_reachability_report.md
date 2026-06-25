# Network Reachability Report

Incident: Service unreachable
Service: edge-api
Root cause: Host binding failure or closed port
Status: fail

## Evidence

- dns_resolution: PASS — localhost resolved to 127.0.0.1
- tcp_reachability: FAIL — TCP connection failed: connection refused
- http_health: FAIL — HTTP health failed: connection refused
- latency: PASS — latency 10ms within threshold 100ms
- dependency_reachability: FAIL — dependency unreachable

## Suggested Remediation

- bind service to 0.0.0.0 instead of localhost
- verify firewall or security group rules
- confirm process is listening on expected port
- restart service after config fix
