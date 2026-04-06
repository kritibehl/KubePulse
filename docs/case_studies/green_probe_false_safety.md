# Green Probe, False Safety

This case study shows a service that appeared healthy through conventional probes while dependency-path degradation still made it unsafe to operate.

KubePulse marked:
- probes healthy: true
- SLO met: false
- safe to operate: false
- recommendation: reroute or block, depending on scenario severity
