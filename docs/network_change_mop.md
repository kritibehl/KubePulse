# Network Change MOP (Method of Procedure)

## Purpose

This document describes a controlled network change workflow for validating service reachability before and after a configuration change.

---

# Scenario

Blocked service port causing production service to become unreachable.

Symptoms:

- DNS resolves successfully
- TCP connection fails
- HTTP health endpoint unavailable
- Service reported unhealthy by KubePulse
- Release decision: **block**

---

# Pre-Change Verification

Validate current network state before making any change.

### DNS Resolution

```bash
dig service.internal
nslookup service.internal
Expected:

Hostname resolves to expected address.
TCP Reachability
nc -vz service.internal 5000

Expected:

TCP connection succeeds.
HTTP Health
curl -v http://service.internal:5000/health

Expected:

HTTP 200.
Listening Ports
ss -ltnp

Expected:

Service listening on expected interface and port.
Firewall Rules
sudo iptables -L -n

Expected:

Expected port allowed.
Planned Change

Simulate a blocked service port by applying a firewall rule that prevents inbound connectivity.

Expected outcome:

TCP connection fails.
HTTP health fails.
KubePulse classifies a reachability failure.
Release decision changes to block.
Rollback Plan

Restore the previous firewall configuration.

Example:

remove temporary firewall rule
restore previous iptables configuration
restart service if required
Post-Change Verification

Repeat validation after rollback.

TCP
nc -vz service.internal 5000

Expected:

Connection succeeds.

HTTP
curl -v http://service.internal:5000/health

Expected:

HTTP 200.

Listening Socket
ss -ltnp

Expected:

Service listening on expected interface.

Success Criteria
DNS resolution succeeds.
TCP connectivity restored.
HTTP health endpoint returns success.
KubePulse reports the service as reachable.
Release decision changes from block to continue when all validation gates pass.
Escalation

Escalate to the Network or SRE owner if:

DNS remains degraded.
TCP connectivity cannot be restored.
Firewall configuration cannot be validated.
Dependency reachability remains unavailable.
Release remains blocked after rollback.
KubePulse Mapping
Network Validation	KubePulse Signal
DNS resolution	dns_resolution
TCP reachability	tcp_reachability
HTTP health	http_health
Firewall validation	blocked_port_iptables
Dependency health	dependency_reachability
Final rollout state	operate_decision / release_decision

