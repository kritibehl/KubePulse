# NetRouteLab

Lightweight Linux/network diagnostics lab for DNS, TCP/IP, traceroute, cURL, and routing-failure analysis.

## Commands to know

```bash
dig example.com
curl -v https://example.com
traceroute example.com
ping example.com
ip route
netstat -an
Run checks
python3 labs/netroute_lab/dns_check.py
python3 labs/netroute_lab/tcp_check.py
python3 labs/netroute_lab/curl_health_check.py
python3 labs/netroute_lab/routing_simulator.py
Resume framing

Built a Linux network diagnostics lab for DNS, TCP/IP, traceroute, cURL, and routing-failure analysis, generating structured incident reports for connectivity troubleshooting.
