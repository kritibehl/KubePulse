# Network Probe Notes

KubePulse includes DNS, TCP, HTTP, and TLS probe artifacts for service-health troubleshooting.

## Probe Layers

| Layer | Probe | Purpose |
|---|---|---|
| DNS | `probes/dns_probe.py` | Validate host resolution |
| TCP | `probes/tcp_probe.py` | Validate port reachability |
| TLS | `probes/tls_probe.py` | Validate handshake, certificate, and cipher |
| HTTP | `probes/http_probe.py` | Validate endpoint response |
| HTTP/2 | `probes/http2_health_probe.md` | Document protocol-level health-check considerations |

## Safe Claim Boundary

KubePulse demonstrates protocol-level troubleshooting concepts for DNS, TCP, TLS, HTTP, and HTTP/2 health checks.

It does not implement or claim QUIC/HTTP3 support.

## Operational Use

These probes help operators distinguish:

- DNS failures
- TCP reachability failures
- TLS handshake/certificate failures
- HTTP endpoint failures
- false-green readiness conditions
- SLO-based release-safety failures

## Example Diagnostic Flow

1. Run DNS probe.
2. Run TCP probe.
3. Run TLS probe for HTTPS endpoints.
4. Run HTTP health probe.
5. Compare app health with SLO/release-gate output.
