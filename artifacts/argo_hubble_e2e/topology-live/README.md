# Topology Live Evidence

Reproduction target:

```text
Kind
  -> Kubernetes
  -> Cilium datapath
  -> client
  -> Kubernetes Service
  -> server
  -> Hubble Relay
  -> captured flow evidence
Pinned datapath version:

Cilium v1.20.0

Primary result:

cat summary.json

Raw flow evidence:

cat hubble_flows.jsonl

Cilium health:

cat cilium_status.txt

This is a controlled local validation environment.
