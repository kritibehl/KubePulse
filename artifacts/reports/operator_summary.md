# Operator Summary

## What happened
A scenario caused degraded dependency-path behavior.

## Why it matters
Green probes can mislead operators when user-facing latency, reachability, or SLOs are still degraded.

## Should traffic continue?
Check `decision_report.json` for the authoritative recommendation.

## What probes got wrong
See `probe_gap_report.md` or probe gap fields in scenario output.

## Likely first fix
Stabilize the degraded dependency path and tighten probe policy if false-green behavior occurred.
