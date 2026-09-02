#!/usr/bin/env bash
set -euo pipefail

LAB="kubepulse-l2-lab"
IMAGE="network_lab-r1"

echo "===== CHECK DOCKER ====="
docker info >/dev/null

docker image inspect "$IMAGE" >/dev/null

echo "===== RESET LAB CONTAINER ====="
docker rm -f "$LAB" >/dev/null 2>&1 || true

docker run -d \
  --name "$LAB" \
  --privileged \
  --network none \
  "$IMAGE" \
  tail -f /dev/null >/dev/null

echo "===== BUILD L2 TOPOLOGY ====="

docker exec "$LAB" bash -lc '
set -euo pipefail

for ns in h10a h20a sw1 sw2 h10b h20b rtr; do
    ip netns add "$ns"
    ip -n "$ns" link set lo up
done

# Host -> SW1
ip link add h10a0 type veth peer name sw1a10
ip link set h10a0 netns h10a
ip link set sw1a10 netns sw1

ip link add h20a0 type veth peer name sw1a20
ip link set h20a0 netns h20a
ip link set sw1a20 netns sw1

# SW1 -> SW2 trunk
ip link add sw1tr type veth peer name sw2tr
ip link set sw1tr netns sw1
ip link set sw2tr netns sw2

# SW2 -> hosts
ip link add h10b0 type veth peer name sw2b10
ip link set h10b0 netns h10b
ip link set sw2b10 netns sw2

ip link add h20b0 type veth peer name sw2b20
ip link set h20b0 netns h20b
ip link set sw2b20 netns sw2

# SW1 -> router trunk
ip link add sw1rtr type veth peer name rtr0
ip link set sw1rtr netns sw1
ip link set rtr0 netns rtr

# VLAN-aware switches
ip -n sw1 link add br0 type bridge vlan_filtering 1
ip -n sw2 link add br0 type bridge vlan_filtering 1

ip -n sw1 link set br0 up
ip -n sw2 link set br0 up

# Attach ports
for p in sw1a10 sw1a20 sw1tr sw1rtr; do
    ip -n sw1 link set "$p" master br0
    ip -n sw1 link set "$p" up
done

for p in sw2tr sw2b10 sw2b20; do
    ip -n sw2 link set "$p" master br0
    ip -n sw2 link set "$p" up
done

# Remove default VLAN 1 from switch ports
for p in sw1a10 sw1a20 sw1tr sw1rtr; do
    ip netns exec sw1 \
      bridge vlan del dev "$p" vid 1 2>/dev/null || true
done

for p in sw2tr sw2b10 sw2b20; do
    ip netns exec sw2 \
      bridge vlan del dev "$p" vid 1 2>/dev/null || true
done

# SW1 access ports
ip netns exec sw1 \
  bridge vlan add dev sw1a10 vid 10 pvid untagged

ip netns exec sw1 \
  bridge vlan add dev sw1a20 vid 20 pvid untagged

# SW1 inter-switch trunk
ip netns exec sw1 \
  bridge vlan add dev sw1tr vid 10

ip netns exec sw1 \
  bridge vlan add dev sw1tr vid 20

# SW1 router trunk
ip netns exec sw1 \
  bridge vlan add dev sw1rtr vid 10

ip netns exec sw1 \
  bridge vlan add dev sw1rtr vid 20

# SW2 trunk
ip netns exec sw2 \
  bridge vlan add dev sw2tr vid 10

ip netns exec sw2 \
  bridge vlan add dev sw2tr vid 20

# SW2 access ports
ip netns exec sw2 \
  bridge vlan add dev sw2b10 vid 10 pvid untagged

ip netns exec sw2 \
  bridge vlan add dev sw2b20 vid 20 pvid untagged

# Hosts
ip -n h10a addr add 10.10.10.11/24 dev h10a0
ip -n h10b addr add 10.10.10.12/24 dev h10b0

ip -n h20a addr add 10.20.20.11/24 dev h20a0
ip -n h20b addr add 10.20.20.12/24 dev h20b0

for pair in \
    "h10a h10a0" \
    "h10b h10b0" \
    "h20a h20a0" \
    "h20b h20b0"
do
    set -- $pair
    ip -n "$1" link set "$2" up
done

# Router-on-a-stick
ip -n rtr link set rtr0 up

ip -n rtr link add \
  link rtr0 \
  name rtr0.10 \
  type vlan id 10

ip -n rtr link add \
  link rtr0 \
  name rtr0.20 \
  type vlan id 20

ip -n rtr addr add \
  10.10.10.1/24 dev rtr0.10

ip -n rtr addr add \
  10.20.20.1/24 dev rtr0.20

ip -n rtr link set rtr0.10 up
ip -n rtr link set rtr0.20 up

ip netns exec rtr \
  sysctl -qw net.ipv4.ip_forward=1

ip netns exec rtr \
  sysctl -qw net.ipv4.conf.all.rp_filter=0

# Host gateways
ip -n h10a route add default via 10.10.10.1
ip -n h10b route add default via 10.10.10.1

ip -n h20a route add default via 10.20.20.1
ip -n h20b route add default via 10.20.20.1
'

echo "===== VERIFY CONFIGURATION ====="

docker exec "$LAB" \
  ip netns exec sw1 bridge vlan show

echo

docker exec "$LAB" \
  ip netns exec sw2 bridge vlan show

echo

docker exec "$LAB" \
  ip -n rtr -br addr

echo
echo "PASS: L2 VLAN and router-on-a-stick lab created"
