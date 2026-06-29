# HTTP Reachability Case Study

## Goal

Show how KubePulse distinguishes web-service contradictions across DNS, TCP, HTTP, latency, and dependency layers.

## Cases

### Case 1: DNS Passes, TCP Fails

**Signal**

- DNS resolution: PASS
- TCP port 5000: FAIL
- HTTP health: FAIL

**Interpretation**

The hostname resolves, but the service is not reachable on the expected port.

**Likely root cause**

Port/firewall/bind issue.

**Suggested remediation**

- confirm process is listening on port 5000
- bind service to `0.0.0.0` instead of `127.0.0.1`
- verify firewall/security group
- restart service after config change

---

### Case 2: TCP Passes, HTTP Fails

**Signal**

- DNS resolution: PASS
- TCP port: PASS
- HTTP health: FAIL

**Interpretation**

The network path is open, but application-level health is failing.

**Likely root cause**

Application or service issue.

**Suggested remediation**

- inspect application logs
- validate health route implementation
- check upstream dependency errors
- confirm app returns expected 2xx health status

---

### Case 3: HTTP 200 but Latency High

**Signal**

- DNS resolution: PASS
- TCP port: PASS
- HTTP health: PASS
- p95/p99 latency: FAIL

**Interpretation**

The service is reachable and returns success, but performance is unsafe for rollout.

**Likely root cause**

Performance degradation, dependency saturation, or retry amplification.

**Suggested remediation**

- review p95/p99 latency drift
- inspect downstream service latency
- check retry behavior
- hold rollout until latency returns within budget

---

### Case 4: Dependency Fails

**Signal**

- local service health: PASS
- dependency reachability: FAIL

**Interpretation**

The service may appear healthy locally but is unsafe because a downstream integration is unavailable.

**Likely root cause**

Downstream integration issue.

**Suggested remediation**

- validate dependency DNS/TCP/HTTP
- check timeout behavior
- fail over if available
- block rollout until dependency health recovers

## Summary

KubePulse classifies contradictions across network and application layers so operators can distinguish reachability, service health, performance, and dependency failures.
