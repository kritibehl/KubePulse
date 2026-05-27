# Blast-Radius Control

## Purpose

KubePulse models staged rollout controls that reduce exposure when a release becomes unsafe.

## Controls

- begin with low-traffic canary wave
- validate edge-site health before expansion
- freeze next wave on alarm state
- block global rollout when dependency health degrades
- preserve release evidence for rollback review

## Example

Wave 1 at `atl1` failed canary validation and entered `ALARM`.

Result:

- wave 2 frozen
- rollback gate triggered
- release decision set to `block`

## Safe Scope

This is a rollout-planning artifact, not proof of live multi-region production operation.
