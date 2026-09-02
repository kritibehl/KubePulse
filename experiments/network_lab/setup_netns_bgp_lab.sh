#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LAB="kubepulse-netns-lab"
IMAGE="kubepulse-network-lab:latest"

cd "$ROOT"

echo "========================================"
echo "BUILD NETWORK LAB IMAGE"
echo "========================================"

docker build \
  -t "$IMAGE" \
  experiments/network_lab/image

echo
echo "========================================"
echo "CREATE LAB CONTAINER"
echo "========================================"

docker rm -f "$LAB" 2>/dev/null || true

docker run -d \
  --name "$LAB" \
  --privileged \
  --network none \
  "$IMAGE" \
  tail -f /dev/null >/dev/null

echo
echo "========================================"
echo "CREATE NETWORK NAMESPACES"
echo "========================================"

docker exec "$LAB" bash -lc '
set -euo pipefail

for ns in h1 r1 r2 h2; do
    ip netns del "$ns" 2>/dev/null || true
    ip netns add "$ns"
    ip -n "$ns" link set lo up
done

# H1 <-> R1
ip link add h1eth type veth peer name r1lan
ip link set h1eth netns h1
ip link set r1lan netns r1

# R1 <-> R2
ip link add r1trans type veth peer name r2trans
ip link set r1trans netns r1
ip link set r2trans netns r2

# R2 <-> H2
ip link add r2lan type veth peer name h2eth
ip link set r2lan netns r2
ip link set h2eth netns h2

# IPv4 addressing
ip -n h1 addr add 10.10.1.10/24 dev h1eth
ip -n r1 addr add 10.10.1.1/24 dev r1lan

ip -n r1 addr add 10.12.0.1/29 dev r1trans
ip -n r2 addr add 10.12.0.2/29 dev r2trans

ip -n r2 addr add 10.20.2.1/24 dev r2lan
ip -n h2 addr add 10.20.2.10/24 dev h2eth

# Interfaces
ip -n h1 link set h1eth up
ip -n r1 link set r1lan up
ip -n r1 link set r1trans up
ip -n r2 link set r2trans up
ip -n r2 link set r2lan up
ip -n h2 link set h2eth up

# Host gateways
ip -n h1 route add default via 10.10.1.1
ip -n h2 route add default via 10.20.2.1

# Router forwarding
for ns in r1 r2; do
    ip netns exec "$ns" sysctl -qw net.ipv4.ip_forward=1
    ip netns exec "$ns" sysctl -qw net.ipv4.conf.all.rp_filter=0
    ip netns exec "$ns" sysctl -qw net.ipv4.conf.default.rp_filter=0
done
'

echo
echo "========================================"
echo "INSTALL FRR PATHSPACES"
echo "========================================"

docker exec "$LAB" bash -lc '
set -euo pipefail

for p in r1 r2; do
    mkdir -p "/etc/frr/$p"
    cp /etc/frr/daemons "/etc/frr/$p/daemons"

    sed -i "s/^bgpd=no/bgpd=yes/" \
        "/etc/frr/$p/daemons"

    sed -i \
        "/^[[:space:]]*watchfrr_options=/d" \
        "/etc/frr/$p/daemons"

    printf "\nwatchfrr_options=\"--netns\"\n" \
        >> "/etc/frr/$p/daemons"

    touch "/etc/frr/$p/vtysh.conf"

    chown frr:frr "/etc/frr/$p/daemons"
    chown frr:frrvty "/etc/frr/$p/vtysh.conf"

    chmod 640 "/etc/frr/$p/daemons"
    chmod 640 "/etc/frr/$p/vtysh.conf"
done
'

docker cp \
  experiments/network_lab/r1/frr.conf \
  "$LAB":/etc/frr/r1/frr.conf

docker cp \
  experiments/network_lab/r2/frr.conf \
  "$LAB":/etc/frr/r2/frr.conf

docker exec "$LAB" bash -lc '
set -euo pipefail

for p in r1 r2; do
    chown frr:frrvty "/etc/frr/$p/frr.conf"
    chmod 640 "/etc/frr/$p/frr.conf"
done
'

echo
echo "========================================"
echo "START FRR"
echo "========================================"

docker exec "$LAB" \
  /usr/lib/frr/frrinit.sh start r1

docker exec "$LAB" \
  /usr/lib/frr/frrinit.sh start r2

echo
echo "Waiting for eBGP convergence..."

success=0

for _ in $(seq 1 30); do
    if docker exec "$LAB" \
        vtysh -N r1 \
        -c "show ip bgp summary" \
        2>/dev/null |
        grep -Eq "10\.12\.0\.2.*[[:space:]]1[[:space:]]+1"; then

        success=1
        break
    fi

    sleep 0.25
done

if [[ "$success" -ne 1 ]]; then
    echo "ERROR: eBGP did not converge"
    docker exec "$LAB" \
        vtysh -N r1 \
        -c "show ip bgp summary" || true
    exit 1
fi

echo
echo "========================================"
echo "VERIFY CONTROL PLANE"
echo "========================================"

docker exec "$LAB" \
  vtysh -N r1 \
  -c "show ip bgp summary"

docker exec "$LAB" \
  vtysh -N r2 \
  -c "show ip bgp summary"

echo
echo "========================================"
echo "VERIFY KERNEL FIB"
echo "========================================"

docker exec "$LAB" \
  ip -n r1 route get 10.20.2.10

docker exec "$LAB" \
  ip -n r2 route get 10.10.1.10

echo
echo "========================================"
echo "VERIFY DATA PLANE"
echo "========================================"

docker exec "$LAB" \
  ip netns exec h1 \
  ping -c 3 10.20.2.10

docker exec "$LAB" \
  ip netns exec h2 \
  ping -c 3 10.10.1.10

echo
echo "PASS: eBGP namespace lab is healthy"
