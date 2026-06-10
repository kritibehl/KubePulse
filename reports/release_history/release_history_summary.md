# Release History Summary

## Totals

- Approved releases: 1
- Blocked releases: 1
- Rollback required: 1

## Release Board

| Release | Service | Decision | Rollback Required | Reason | p95 Delta | p99 Delta | Readiness |
|---|---|---|---:|---|---:|---:|---|
| rel-2026-04-001 | edge-api | blocked | False | dependency cascade + latency drift | 333.33% | 275.0% | unsafe |
| rel-2026-04-002 | auth-service | rollback_required | True | DNS failure caused dependency reachability loss | 210.0% | 240.0% | unsafe |
| rel-2026-04-003 | catalog-api | approved | False | baseline within rollout budget | 4.5% | 7.2% | safe |
