from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta, timezone
import heapq
import uuid

@dataclass
class LinkState:
    src: str
    dst: str
    weight: float
    up: bool = True

class Topology:
    def __init__(self, links: List[LinkState]):
        self.links = links

    def adjacency(self) -> Dict[str, List[Tuple[str, float]]]:
        adj: Dict[str, List[Tuple[str, float]]] = {}
        for l in self.links:
            if not l.up:
                continue
            adj.setdefault(l.src, []).append((l.dst, l.weight))
            adj.setdefault(l.dst, []).append((l.src, l.weight))
        return adj

    def shortest_path(self, src: str, dst: str) -> Tuple[Optional[List[str]], float]:
        adj = self.adjacency()
        if src not in adj or dst not in adj:
            return None, float("inf")

        pq = [(0.0, src, [src])]
        seen = {}

        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in seen and seen[node] <= cost:
                continue
            seen[node] = cost
            if node == dst:
                return path, cost
            for nxt, w in adj.get(node, []):
                heapq.heappush(pq, (cost + w, nxt, path + [nxt]))
        return None, float("inf")

    def set_link_state(self, a: str, b: str, up: bool):
        for l in self.links:
            if {l.src, l.dst} == {a, b}:
                l.up = up

    def set_link_weight(self, a: str, b: str, weight: float):
        for l in self.links:
            if {l.src, l.dst} == {a, b}:
                l.weight = weight

def default_topology() -> Topology:
    return Topology([
        LinkState("edge", "router-a", 1.0, True),
        LinkState("edge", "router-b", 2.0, True),
        LinkState("router-a", "api", 1.0, True),
        LinkState("router-b", "api", 1.0, True),
        LinkState("api", "auth", 1.0, True),
        LinkState("auth", "downstream", 1.0, True),
        LinkState("router-a", "auth", 3.0, True),
        LinkState("router-b", "auth", 2.0, True),
    ])

def _timeline_event(offset_s: int, kind: str, detail: str) -> dict:
    t = datetime.now(timezone.utc) + timedelta(seconds=offset_s)
    return {"ts": t.isoformat(), "kind": kind, "detail": detail}

def run_topology_scenario(name: str) -> dict:
    topo = default_topology()
    baseline_path, baseline_cost = topo.shortest_path("edge", "downstream")
    events = [_timeline_event(0, "baseline_path", f"{baseline_path} cost={baseline_cost}")]
    path_changes_total = 0
    unreachable_windows_total = 0
    degraded_path_requests_total = 0
    convergence_seconds = 0.0
    final_path = baseline_path
    final_cost = baseline_cost
    broken_hop = None
    reroute_detail = None
    partial_recovery = False

    if name == "link_failure_failover":
        topo.set_link_state("router-a", "api", False)
        broken_hop = "router-a <-> api"
        events.append(_timeline_event(1, "link_down", broken_hop))
        new_path, new_cost = topo.shortest_path("edge", "downstream")
        if new_path != baseline_path:
            path_changes_total += 1
            degraded_path_requests_total += 12
            convergence_seconds = 2.4
            reroute_detail = {"old_path": baseline_path, "new_path": new_path}
            events.append(_timeline_event(3, "reroute", f"{baseline_path} -> {new_path}"))
            final_path, final_cost = new_path, new_cost
        else:
            partial_recovery = True

    elif name == "link_flap":
        broken_hop = "router-a <-> api"
        for i in range(3):
            topo.set_link_state("router-a", "api", False)
            events.append(_timeline_event(1 + i * 2, "link_down", broken_hop))
            topo.shortest_path("edge", "downstream")
            topo.set_link_state("router-a", "api", True)
            events.append(_timeline_event(2 + i * 2, "link_up", broken_hop))
            path_changes_total += 2
        degraded_path_requests_total = 18
        convergence_seconds = 6.0
        final_path, final_cost = topo.shortest_path("edge", "downstream")
        reroute_detail = {"old_path": baseline_path, "new_path": final_path}

    elif name == "asymmetric_path":
        topo.set_link_weight("edge", "router-a", 5.0)
        topo.set_link_weight("edge", "router-b", 1.0)
        broken_hop = "edge <-> router-a"
        events.append(_timeline_event(1, "weight_change", "edge-router-a weight 1.0 -> 5.0"))
        new_path, new_cost = topo.shortest_path("edge", "downstream")
        if new_path != baseline_path:
            path_changes_total += 1
            degraded_path_requests_total = 9
            convergence_seconds = 1.7
            reroute_detail = {"old_path": baseline_path, "new_path": new_path}
            events.append(_timeline_event(2, "reroute", f"{baseline_path} -> {new_path}"))
            final_path, final_cost = new_path, new_cost

    elif name == "blackhole":
        topo.set_link_state("api", "auth", False)
        topo.set_link_state("router-a", "auth", False)
        topo.set_link_state("router-b", "auth", False)
        broken_hop = "auth ingress"
        events.append(_timeline_event(1, "link_down", "api-auth, router-a-auth, router-b-auth"))
        new_path, new_cost = topo.shortest_path("edge", "downstream")
        if new_path is None:
            unreachable_windows_total = 1
            degraded_path_requests_total = 25
            convergence_seconds = 0.0
            final_path, final_cost = None, float("inf")
            events.append(_timeline_event(2, "unreachable", "No path from edge to downstream"))
        else:
            final_path, final_cost = new_path, new_cost

    else:
        raise ValueError(f"Unsupported topology scenario: {name}")

    availability_pct = 0.0 if final_path is None else (92.0 if degraded_path_requests_total else 100.0)
    p95_ms = 240.0 if final_path == baseline_path else 540.0
    p99_ms = 420.0 if final_path == baseline_path else 880.0
    extra_latency_ms = max(0.0, (final_cost - baseline_cost) * 80.0) if final_path else 0.0

    return {
        "run_id": uuid.uuid4().hex,
        "scenario": name,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": (datetime.now(timezone.utc) + timedelta(seconds=max(1, int(convergence_seconds) + 1))).isoformat(),
        "success": final_path is not None,
        "status": "pass" if final_path is not None else "fail",
        "topology_nodes": ["edge", "router-a", "router-b", "api", "auth", "downstream"],
        "baseline_path": baseline_path,
        "baseline_path_cost": baseline_cost,
        "final_path": final_path,
        "final_path_cost": None if final_path is None else final_cost,
        "path_change_timeline": events,
        "broken_hop": broken_hop,
        "reroute_detail": reroute_detail,
        "partial_recovery": partial_recovery,
        "convergence_seconds": convergence_seconds,
        "path_changes_total": path_changes_total,
        "unreachable_windows_total": unreachable_windows_total,
        "degraded_path_requests_total": degraded_path_requests_total,
        "availability_achieved_pct_simulated": availability_pct,
        "latency_p50_ms": 120.0 if final_path == baseline_path else 220.0,
        "latency_p95_ms": p95_ms,
        "latency_p99_ms": p99_ms,
        "error_rate": 0.0 if final_path == baseline_path else (0.02 if final_path else 0.18),
        "cross_zone_degradation_pct": 0.0 if final_path == baseline_path else 18.0,
        "path_recovery_time_seconds": convergence_seconds,
        "network_availability_gap_pct": max(0.0, 100.0 - availability_pct),
        "path_extra_latency_ms": extra_latency_ms,
        "recommendation": (
            "Reroute validated; monitor convergence and degraded path latency."
            if final_path is not None else
            "Blackhole detected; restore broken hop or alternate auth/downstream path."
        ),
        "readiness_before": "ready",
        "readiness_after": "ready-but-degraded" if final_path and final_path != baseline_path else ("not-ready" if final_path is None else "ready"),
        "readiness_false_positive": bool(final_path is not None and final_path != baseline_path),
        "pass_fail_reason": (
            "Topology converged to alternate path." if final_path and final_path != baseline_path
            else ("Topology remained healthy." if final_path else "Downstream path unreachable after link event.")
        ),
        "pod_name": "topology-lab",
        "namespace": "default",
        "probe_mismatch": bool(final_path is not None and final_path != baseline_path),
        "restart_count": 0,
    }
