# KubePulse Network Lab

KubePulse Network Lab extends KubePulse with a Linux namespace/container-based service network used to run repeatable service-to-service failure experiments under controlled network degradation.

## Goal

Demonstrate:
- Linux / Unix networking
- TCP/IP behavior under failure
- DNS and service discovery degradation
- service-to-service communication issues
- path degradation and recovery
- network monitoring
- automated remediation guidance
- repeatable baseline vs degraded experiments

## Topology

Services:
- edge / gateway
- api-service
- auth-service
- datastore-mock

## Initial Failure Scenarios
1. DNS resolution failure
2. packet loss / latency injection
3. partial service partition
4. intermittent TCP reset / connection churn

## Core Metrics
- DNS success rate
- TCP connect latency
- request success rate
- p95 latency
- retry count
- recovery time
- impacted downstream services
- false-positive health signals
- remediation recommendation

## Safe Claims
This lab supports interview-defensible discussion of:
- Linux-based network fault simulation
- service-to-service failure diagnosis
- DNS/TCP/HTTP degradation analysis
- blast-radius inference
- automated remediation guidance
- recovery instrumentation under degraded network conditions

## Multi-Hop Path and Failover

KubePulse Network Lab now supports a multi-hop dependency path:

`edge -> api-service -> auth-service -> router-hop -> datastore`

with alternate primary/secondary datastore paths to test:

- primary path down
- secondary path takeover
- path flapping
- asymmetric latency across hops

## Network Measurements

The lab captures:
- DNS lookup success/failure
- TCP connect latency
- request success/failure split
- p50/p95 latency
- recovery/convergence timing
- degraded-hop detection
- downstream blast radius
