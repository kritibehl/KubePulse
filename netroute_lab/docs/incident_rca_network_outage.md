# Incident RCA: Network Path Degradation

## Incident Summary

The checkout-to-payments path showed elevated packet loss and latency during release validation.

## Detection

NetRouteLab flagged:

- packet-loss threshold violation
- latency threshold violation
- reduced capacity headroom
- impacted payments path

## Probable Cause

The degraded network segment between `svc-checkout` and `svc-payments` exceeded packet-loss and latency thresholds.

## Recommendation

- reroute traffic away from degraded path
- repair or replace degraded segment
- re-run capacity validation before release continuation

## Outcome

Release should remain blocked until network validation returns PASS.
