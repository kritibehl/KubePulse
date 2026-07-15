# Network Service Health Report

- Service: `orders-api`
- Proxy-style path: `client -> ingress/proxy -> orders-api -> postgresql`
- Operate decision: `unsafe_to_operate`
- Release decision: `block`

## Diagnostic Checklist

| Check | Status | Evidence |
|---|---|---|
| dns | pass | service.internal resolved to 10.0.1.15 |
| tcp | pass | TCP connection succeeded |
| tls | pass | TLS handshake succeeded |
| http | pass | HTTP response returned 200 |
| latency_budget | fail | latency 620ms exceeded 300ms budget |
| dependency_health | fail | postgresql dependency unreachable |

## Probable Root Causes

- performance degradation or overloaded dependency
- downstream integration failure

## Incident Escalation

escalate to service, network, or dependency owner based on failed layer
