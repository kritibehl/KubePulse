# HTTP/2 Health Probe Notes

KubePulse includes HTTP-level health checks and protocol troubleshooting notes for release validation workflows.

## Scope

This document covers HTTP/2 health-check considerations only.

It does not claim QUIC or HTTP/3 support.

## What to Validate

- TLS handshake succeeds
- certificate is valid
- HTTP endpoint responds successfully
- health endpoint returns 2xx
- client/server protocol negotiation is understood
- failures are classified separately from app-level readiness failures

## Example Checks

```bash
curl -v --http2 https://example.com/health
python probes/tls_probe.py example.com 443
Failure Categories
Failure	Meaning
DNS resolution failure	host cannot be resolved
TCP connection failure	service/port unreachable
TLS failure	certificate, handshake, or trust issue
HTTP non-2xx	endpoint reachable but unhealthy
App readiness mismatch	health check passes while SLO gate fails
Why This Matters

Protocol-level checks help separate connectivity, TLS, and HTTP failures from application-level release-safety failures.
