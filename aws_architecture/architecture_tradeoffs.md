# Architecture Tradeoffs

## Availability

Deployment waves reduce blast radius by validating one site or traffic slice before expanding rollout.

## Cost

S3-style artifact storage is low-cost for release evidence. CloudWatch-style alarms and dashboards should focus on high-signal rollout metrics to avoid noisy monitoring cost.

## Security

Release artifacts should avoid storing secrets. Deployment policy validation should block missing TLS, missing authentication, and insecure environment variables before release continuation.

## Rollback

Rollback gates should freeze later waves when canary validation, CloudWatch alarms, or dependency-risk scores indicate unsafe rollout behavior.

## Observability

CloudWatch/Prometheus/Grafana-style signals should preserve deployment ID, site, wave, alarm state, and rollback decision for post-incident analysis.

## Safe Scope

These are architecture tradeoff notes for a local release-safety platform prototype.
