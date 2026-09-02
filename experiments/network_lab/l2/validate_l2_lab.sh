#!/usr/bin/env bash
set -euo pipefail

LAB="kubepulse-l2-lab"
ARTIFACTS="artifacts/network_lab/l2"

mkdir -p "$ARTIFACTS"

pass() {
    echo "PASS: $1"
}

fail() {
    echo "FAIL: $1"
    exit 1
}

echo "========================================"
echo "1. SAME-VLAN BASELINE"
echo "========================================"

docker exec "$LAB" \
  ip netns exec h10a \
  ping -c 2 10.10.10.12 >/dev/null ||
  fail "VLAN 10 baseline"

pass "VLAN 10 same-VLAN forwarding"

docker exec "$LAB" \
  ip netns exec h20a \
  ping -c 2 10.20.20.12 >/dev/null ||
  fail "VLAN 20 baseline"

pass "VLAN 20 same-VLAN forwarding"

echo
echo "========================================"
echo "2. VLAN AND FDB STATE"
echo "========================================"

docker exec "$LAB" \
  ip netns exec sw1 bridge vlan show

docker exec "$LAB" \
  ip netns exec sw2 bridge vlan show

docker exec "$LAB" \
  ip netns exec sw1 bridge fdb show br br0 |
grep -q "vlan 10" ||
  fail "SW1 VLAN 10 FDB learning"

docker exec "$LAB" \
  ip netns exec sw1 bridge fdb show br br0 |
grep -q "vlan 20" ||
  fail "SW1 VLAN 20 FDB learning"

pass "MAC/FDB learning"

echo
echo "========================================"
echo "3. 802.1Q TRUNK EVIDENCE"
echo "========================================"

docker exec -d "$LAB" bash -lc '
ip netns exec sw1 \
  timeout 6 tcpdump -U -enn -i sw1tr \
  -w /tmp/l2_trunk_tags.pcap
'

sleep 1

docker exec "$LAB" \
  ip netns exec h10a \
  ping -c 1 10.10.10.12 >/dev/null

docker exec "$LAB" \
  ip netns exec h20a \
  ping -c 1 10.20.20.12 >/dev/null

sleep 6

TRUNK_DECODE="$(
docker exec "$LAB" \
  tcpdump -enn -vv \
  -r /tmp/l2_trunk_tags.pcap \
  2>/dev/null
)"

grep -q "vlan 10" <<<"$TRUNK_DECODE" ||
  fail "VLAN 10 tag absent from trunk capture"

grep -q "vlan 20" <<<"$TRUNK_DECODE" ||
  fail "VLAN 20 tag absent from trunk capture"

docker cp \
  "$LAB":/tmp/l2_trunk_tags.pcap \
  "$ARTIFACTS/l2_trunk_tags.pcap" >/dev/null

pass "802.1Q VLAN 10 and VLAN 20 tags captured"

echo
echo "========================================"
echo "4. TRUE VLAN ISOLATION"
echo "========================================"

docker exec "$LAB" \
  ip -n h10a addr add \
  192.0.2.10/24 dev h10a0

docker exec "$LAB" \
  ip -n h20a addr add \
  192.0.2.20/24 dev h20a0

if docker exec "$LAB" \
  ip netns exec h10a \
  ping -c 2 -W 1 192.0.2.20 >/dev/null 2>&1
then
    fail "different VLANs unexpectedly bridged"
fi

docker exec "$LAB" \
  ip -n h10a addr del \
  192.0.2.10/24 dev h10a0

docker exec "$LAB" \
  ip -n h20a addr del \
  192.0.2.20/24 dev h20a0

pass "VLAN 10 and VLAN 20 remain separate broadcast domains"

echo
echo "========================================"
echo "5. SELECTIVE TRUNK FAILURE"
echo "========================================"

docker exec "$LAB" \
  ip netns exec sw2 \
  bridge vlan del dev sw2tr vid 10

docker exec -d "$LAB" bash -lc '
ip netns exec sw1 \
  timeout 6 tcpdump -U -enn -i sw1tr \
  -w /tmp/vlan10_trunk_fault.pcap
'

sleep 1

if docker exec "$LAB" \
  ip netns exec h10a \
  ping -c 2 -W 1 10.10.10.12 >/dev/null 2>&1
then
    fail "VLAN 10 should fail after trunk membership removal"
fi

pass "VLAN 10 failed after selective trunk fault"

docker exec "$LAB" \
  ip netns exec h20a \
  ping -c 2 10.20.20.12 >/dev/null ||
  fail "VLAN 20 should remain healthy"

pass "VLAN 20 remained healthy"

docker exec "$LAB" \
  ip -n sw1 -br link show sw1tr |
grep -q "LOWER_UP" ||
  fail "SW1 trunk physical state"

docker exec "$LAB" \
  ip -n sw2 -br link show sw2tr |
grep -q "LOWER_UP" ||
  fail "SW2 trunk physical state"

pass "physical trunk remained UP"

docker exec "$LAB" \
  ip netns exec h10a \
  ping -c 1 -W 1 10.10.10.12 >/dev/null 2>&1 || true

sleep 6

docker cp \
  "$LAB":/tmp/vlan10_trunk_fault.pcap \
  "$ARTIFACTS/vlan10_trunk_fault.pcap" >/dev/null

echo
echo "SW2 fault-state VLAN table:"
docker exec "$LAB" \
  ip netns exec sw2 bridge vlan show

echo
echo "========================================"
echo "6. ROLLBACK"
echo "========================================"

docker exec "$LAB" \
  ip netns exec sw2 \
  bridge vlan add dev sw2tr vid 10

docker exec "$LAB" \
  ip netns exec h10a \
  ping -c 3 10.10.10.12 >/dev/null ||
  fail "VLAN 10 rollback"

pass "VLAN 10 connectivity restored"

docker exec "$LAB" \
  ip netns exec h20a \
  ping -c 3 10.20.20.12 >/dev/null ||
  fail "VLAN 20 regression"

pass "VLAN 20 remained healthy after rollback"

echo
echo "========================================"
echo "7. INTER-VLAN ROUTING"
echo "========================================"

docker exec "$LAB" \
  ip netns exec h10a \
  ping -c 3 10.20.20.12 >/dev/null ||
  fail "VLAN 10 -> VLAN 20 routing"

docker exec "$LAB" \
  ip netns exec h20b \
  ping -c 3 10.10.10.11 >/dev/null ||
  fail "VLAN 20 -> VLAN 10 routing"

pass "bidirectional inter-VLAN routing"

echo
echo "========================================"
echo "8. ROUTER-ON-A-STICK PCAP"
echo "========================================"

docker exec -d "$LAB" bash -lc '
ip netns exec rtr \
  timeout 6 tcpdump -U -enn -i rtr0 \
  -w /tmp/inter_vlan_routing.pcap
'

sleep 1

docker exec "$LAB" \
  ip netns exec h10a \
  ping -c 1 10.20.20.12 >/dev/null

sleep 6

ROUTED_DECODE="$(
docker exec "$LAB" \
  tcpdump -enn -vv \
  -r /tmp/inter_vlan_routing.pcap \
  2>/dev/null
)"

grep -q "vlan 10" <<<"$ROUTED_DECODE" ||
  fail "routed packet missing VLAN 10"

grep -q "vlan 20" <<<"$ROUTED_DECODE" ||
  fail "routed packet missing VLAN 20"

grep -q "10.10.10.11 > 10.20.20.12" <<<"$ROUTED_DECODE" ||
  fail "inter-VLAN ICMP flow missing"

docker cp \
  "$LAB":/tmp/inter_vlan_routing.pcap \
  "$ARTIFACTS/inter_vlan_routing.pcap" >/dev/null

pass "router-on-a-stick packet transition captured"

echo
echo "========================================"
echo "L2 VALIDATION COMPLETE"
echo "========================================"

echo "PASS: VLAN access/trunk behavior"
echo "PASS: MAC/FDB learning"
echo "PASS: 802.1Q tagging"
echo "PASS: VLAN isolation"
echo "PASS: selective trunk fault isolation"
echo "PASS: rollback"
echo "PASS: inter-VLAN routing"
echo "PASS: packet-capture evidence"
