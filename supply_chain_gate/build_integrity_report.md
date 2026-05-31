# Build Integrity Report

## Result

KubePulse blocked rollout continuation because the deployment artifact lacked signing evidence.

## Checks

| Check | Status |
|---|---|
| provenance present | pass |
| signed artifact | fail |
| dependency review | pass |
| reproducible build | pass |

## Release Decision

`block`
