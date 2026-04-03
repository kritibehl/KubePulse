# Path Trace Correlation

KubePulse exposes before/after path reasoning for topology and degraded-path scenarios.

## What it shows
- which hop degraded
- where latency increased
- what path changed
- before/after path timeline
- trace-style hop event sequence

## Example interpretation
- baseline path: `edge -> router-a -> api -> auth -> downstream`
- final path: `edge -> router-a -> auth -> downstream`
- broken hop: `router-a<->api`
- degraded hop: `router-a->auth`
- path shift summary: rerouted around failed hop, but user-facing latency still increased
