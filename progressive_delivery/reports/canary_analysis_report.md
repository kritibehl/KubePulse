# Canary Analysis Report

| Step | p95 Regression | Analysis Result | Rollback |
|---|---:|---|---|
| 10% traffic | +12% | passed | false |
| 25% traffic | +184% | failed | true |

## Decision

Rollback triggered because p95 regression exceeded the canary analysis threshold.
