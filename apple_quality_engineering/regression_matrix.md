# Regression Matrix

| Feature | Edge Case | Expected Behavior | Risk | CI Status |
|---|---|---|---|---|
| release gate | safe_to_operate=false | block | high | pass |
| canary rollout | p95 > budget | block | high | pass |
| deployment wave | alarm=ALARM | freeze next wave | high | pass |
| network gate | packet loss > threshold | block | high | pass |
| security gate | missing TLS/auth | block | critical | pass |
| capacity gate | p99 > budget | block | high | pass |
