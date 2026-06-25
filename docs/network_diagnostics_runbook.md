# Network Diagnostics Runbook

## Purpose

KubePulse validates whether a service is reachable and safe to operate even when the process is running.

## Checks

- DNS resolution
- TCP port reachability
- HTTP / HTTPS health
- latency threshold
- packet loss
- timeout behavior
- host / port binding failures
- dependency reachability

## Common Failure: Service Running but Unreachable

A service can be running but still unhealthy when:

- DNS does not resolve
- the expected port is closed
- the service binds to localhost instead of 0.0.0.0
- HTTP health endpoint fails
- latency exceeds threshold
- dependency is unreachable

## Example Incident

Incident: Service unreachable  
Root cause: Host binding failure

Evidence:

- DNS resolution: PASS
- TCP port 5000: FAIL
- HTTP health: FAIL
- Process expected port: 5000

Suggested remediation:

- bind service to 0.0.0.0
- verify firewall or security group
- restart service
- confirm the service listens on the expected port

## Operator Flow

1. Check DNS.
2. Check TCP reachability.
3. Check HTTP health.
4. Check latency and packet loss.
5. Check dependency reachability.
6. Classify root cause.
7. Apply remediation.
8. Re-run diagnostics.
