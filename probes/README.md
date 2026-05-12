# Health Probes

Simple DNS, TCP, and HTTP probes for service-health troubleshooting.

Examples:

```bash
python probes/dns_probe.py localhost
python probes/tcp_probe.py localhost 8000
python probes/http_probe.py http://localhost:8000/health
