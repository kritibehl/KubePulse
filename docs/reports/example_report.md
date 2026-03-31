# Example Resilience Report

## Scenario
DNS failure affecting downstream auth dependency

## Observed State
- request success collapsed from **25/25** to **0/25**
- downstream dependency resolution failed
- service path became unavailable end-to-end

## Probe Integrity
A service may continue to appear superficially healthy while downstream dependency availability is broken.

## Rollout Risk Interpretation
**Unsafe to continue rollout or assume recovery.**
Dependency reachability is still broken, so traffic restoration would be misleading.

## Recommendation
- validate service discovery / DNS path
- confirm downstream dependency resolution from upstream services
- block further rollout until dependency path is restored
