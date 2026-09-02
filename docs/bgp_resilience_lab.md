# eBGP Resilience and Convergence Lab

## Objective

Validate BGP route advertisement, explicit routing policy, Linux
RIB/FIB propagation, route withdrawal, end-to-end reachability,
and recovery under a controlled two-AS topology.

## Topology

```text
H1
10.10.1.10/24
       |
       | default 10.10.1.1
       |
R1 — AS65001
10.10.1.1/24
10.12.0.1/29
       |
       | eBGP
       | TCP/179
       |
10.12.0.2/29
R2 — AS65002
10.20.2.1/24
       |
       |
H2
10.20.2.10/24
The topology uses Linux network namespaces and veth pairs so the
routing data plane is independent of Docker Desktop bridge isolation.

BGP Policy

R1:

originates 10.10.1.0/24
accepts only 10.20.2.0/24
exports only 10.10.1.0/24

R2:

originates 10.20.2.0/24
accepts only 10.10.1.0/24
exports only 10.20.2.0/24

Explicit prefix lists satisfy FRR's eBGP policy requirement rather
than disabling route-policy protection.

Baseline

The static test routes were removed before FRR was started.

R1 learned:

10.20.2.0/24 via 10.12.0.2 proto bgp metric 20

R2 learned:

10.10.1.0/24 via 10.12.0.1 proto bgp metric 20

The BGP peers reached Established, and bidirectional H1/H2 traffic
completed with 0% packet loss.

Traceroute from H1 to H2 showed:

10.10.1.1
10.12.0.2
10.20.2.10
Failure Injection

R2's advertisement of 10.20.2.0/24 was withdrawn without shutting
down the BGP peer.

The BGP session remained Established while R1's received prefix count
changed from one to zero.

A TCP/179 packet capture decoded the BGP UPDATE as:

Update Message
Withdrawn routes:
  10.20.2.0/24

After withdrawal:

the prefix disappeared from R1's BGP RIB;
it disappeared from the FRR routing table;
it disappeared from the Linux kernel FIB;
H1 received Destination Net Unreachable.

The advertisement was then restored. The BGP prefix, kernel route,
and end-to-end reachability all recovered.

Ten-Run Benchmark

Ten successful withdrawal/restore experiments were executed.

Observed route restoration
Signal	Median	p95
BGP RIB restoration	141.661 ms	162.499 ms
Linux FIB restoration	198.267 ms	215.834 ms
Data-plane recovery	250.553 ms	270.356 ms
Observed withdrawal
Signal	Median	p95
BGP route absent	346.618 ms	409.402 ms
Linux FIB route absent	197.888 ms	327.356 ms
Data-plane failure	249.608 ms	296.524 ms
Measurement Caveat

Measurements use Python's monotonic clock but observe state using
host-driven docker exec commands.

Therefore the values include command startup and polling overhead.
They represent lab-observed convergence/recovery latency rather than
wire-speed BGP implementation latency.

The individual BGP, FIB, and data-plane observation timestamps must
not be interpreted as exact internal causal ordering.

The most useful end-to-end benchmark is the observed data-plane
recovery distribution.

Evidence
artifacts/network_lab/bgp_withdrawal_manual.pcap
artifacts/network_lab/bgp_convergence_single_run.json
artifacts/network_lab/bgp_convergence_benchmark.json
artifacts/network_lab/bgp_convergence_run_01.json through
bgp_convergence_run_10.json
Reproduction
./experiments/network_lab/setup_netns_bgp_lab.sh

python3 \
  experiments/network_lab/measure_bgp_convergence.py

python3 \
  experiments/network_lab/benchmark_bgp_convergence.py

./experiments/network_lab/teardown_netns_bgp_lab.sh

