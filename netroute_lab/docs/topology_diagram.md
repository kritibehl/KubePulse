# Network Topology Diagram

```text
                 +----------------+
                 |  dns-resolver  |
                 +--------+-------+
                          ^
                          |
                          |
+---------------+         |
| edge-gateway  +---------+
+-------+-------+
        |
        |
        v
+---------------+
| svc-checkout  |
+------+--------+
       |                     degraded path
       |------------------------------------------+
       |                                          |
       v                                          v
+---------------+                      +----------------+
| svc-inventory |                      | svc-payments   |
+---------------+                      +----------------+
Degraded Segment

The svc-checkout -> svc-payments link exceeds:

latency threshold
packet-loss threshold
Operational Outcome
RCA generated
release validation failed
remediation recommended
