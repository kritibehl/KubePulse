# NetRouteLab

NetRouteLab is a scoped network automation validation lab inside KubePulse.

It validates network topology metadata, routing paths, latency thresholds, packet-loss conditions, and capacity headroom during release-safety and incident-analysis workflows.

## What It Validates

- DNS/TCP-oriented service paths
- routing-path health
- latency thresholds
- packet-loss thresholds
- capacity headroom
- degraded-link detection
- repair/replace recommendations
- RCA-style incident analysis

## Sample Topology

| Source | Target | Latency | Packet Loss | Capacity |
|---|---|---:|---:|---:|
| edge-gateway | svc-checkout | 18 ms | 0.1% | 1000 Mbps |
| svc-checkout | svc-inventory | 45 ms | 1.2% | 400 Mbps |
| svc-checkout | svc-payments | 92 ms | 4.8% | 250 Mbps |

## Example Degraded Link

The `svc-checkout -> svc-payments` path exceeds:
- latency threshold
- packet-loss threshold

This triggers:
- RCA findings
- degraded-link detection
- release-block recommendation
- repair/replace remediation guidance

## Capacity Threshold Example

| Scenario | Headroom % | Result |
|---|---:|---|
| normal_release_traffic | acceptable | PASS |
| checkout_to_payments_degraded | low headroom | FAIL |
| inventory_spike | near threshold | WARN |

## RCA Output

NetRouteLab generates:
- network validation reports
- capacity analysis reports
- RCA-style outage notes
- remediation recommendations

## Repair / Replace Recommendation

If packet loss or latency thresholds exceed policy:
- reroute traffic away from degraded link
- repair or replace degraded network segment
- re-run validation before release continuation

## How To Run

```bash
python3 netroute_lab/run_network_validation.py
Output Artifacts
reports/network_validation_report.md
reports/capacity_analysis_report.md
reports/network_validation_summary.json
Safe Scope

NetRouteLab is a simulation and validation lab.

It does not claim:

production WAN control
BGP automation
SDN controller implementation
real router programming
