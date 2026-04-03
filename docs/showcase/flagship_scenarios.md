# Flagship Scenario Artifacts

## 1. Link Failure Failover
- broken hop: `router-a<->api`
- path shift: `edge -> router-a -> api -> auth -> downstream` -> `edge -> router-a -> auth -> downstream`
- convergence: **2.4s**
- path changes: **1**
- degraded-path requests: **12**
- safe to operate: **no**

## 2. Blackhole
- downstream path became unreachable
- unreachable window: **18.0s**
- availability: **0%**
- degraded-path requests: **25**
- recommendation: **block**
- safe to operate: **no**

## 3. Link Flap
- repeated route churn
- convergence: **6.0s**
- path changes: **6**
- degraded-path requests: **18**
- probes remained healthy during instability
- safe to operate: **no**

## 4. Asymmetric Path
- path shifted to alternate route under weight change
- convergence: **1.7s**
- path changes: **1**
- degraded-path requests: **9**
- p95 drift: **125%**
- safe to operate: **no**
