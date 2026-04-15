from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import heapq
import uuid

@dataclass
class Link:
    a: str
    b: str
    weight: float
    up: bool = True

class Topology:
    def __init__(self, links: List[Link]):
        self.links = links

    def adjacency(self) -> Dict[str, List[Tuple[str, float]]]:
        adj: Dict[str, List[Tuple[str, float]]] = {}
        for l in self.links:
            if not l.up:
                continue
            adj.setdefault(l.a, []).append((l.b, l.weight))
            adj.setdefault(l.b, []).append((l.a, l.weight))
        return adj

    def shortest_path(self, src: str, dst: str) -> Tuple[Optional[List[str]], float]:
        adj = self.adjacency()
        if src not in adj or dst not in adj:
            return None, float("inf")

        pq: List[Tuple[float, str, List[str]]] = [(0.0, src, [src])]
        best: Dict[str, float] = {}

        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in best and best[node] <= cost:
                continue
            best[node] = cost
            if node == dst:
                return path, cost
            for nxt, w in adj.get(node, []):
                heapq.heappush(pq, (cost + w, nxt, path + [nxt]))
        return None, float("inf")

    def set_link_state(self, x: str, y: str, up: bool):
        for l in self.links:
            if {l.a, l.b} == {x, y}:
                l.up = up

    def set_link_weight(self, x: str, y: str, weight: float):
        for l in self.links:
            if {l.a, l.b} == {x, y}:
                l.weight = weight

def default_topology() -> Topology:
    return Topology([
        Link("edge", "router-a", 1.0, True),
        Link("edge", "router-b", 2.0, True),
        Link("router-a", "api", 1.0, True),
        Link("router-b", "api", 1.0, True),
        Link("api", "auth", 1.0, True),
        Link("auth", "downstream", 1.0, True),
        Link("router-a", "auth", 3.0, True),
        Link("router-b", "auth", 2.0, True),
    ])

def _evt(offset_s: int, kind: str, detail: str) -> dict:
    ts = datetime.now(timezone.utc) + timedelta(seconds=offset_s)
    return {"ts": ts.isoformat(), "kind": kind, "detail": detail}

def _decision_artifact(
    *,
    scenario: str,
    probes_healthy: bool,
    slo_met: bool,
    safe_to_operate: bool,
    what_probes_missed: List[str],
    recommendation: str,
) -> dict:
    return {
        "scenario": scenario,
        "probes_say_healthy": probes_healthy,
        "slo_met": slo_met,
        "safe_to_operate": safe_to_operate,
        "what_probes_missed": what_probes_missed,
        "recommendation_action": recommendation,
    }

def run_topology_decision_scenario(name: str) -> dict:
    topo = default_topology()
    started = datetime.now(timezone.utc)

    baseline_path, baseline_cost = topo.shortest_path("edge", "downstream")
    timeline = [_evt(0, "baseline_path", f"{baseline_path} cost={baseline_cost}")]

    path_changes_total = 0
    unreachable_window_seconds = 0.0
    degraded_path_requests_total = 0
    convergence_seconds = 0.0
    final_path = baseline_path
    final_cost = baseline_cost
    broken_hop = None
    reroute_detail = None
    path_recovery_status = "stable"
    probes_false_positive = False
    what_probes_missed: List[str] = []

    if name == "link_failure_failover":
        broken_hop = "router-a<->api"
        topo.set_link_state("router-a", "api", False)
        timeline.append(_evt(1, "link_down", broken_hop))
        new_path, new_cost = topo.shortest_path("edge", "downstream")
        if new_path is not None and new_path != baseline_path:
            path_changes_total = 1
            degraded_path_requests_total = 12
            convergence_seconds = 2.4
            path_recovery_status = "rerouted"
            reroute_detail = {"old_path": baseline_path, "new_path": new_path}
            timeline.append(_evt(3, "reroute", f"{baseline_path} -> {new_path}"))
            final_path, final_cost = new_path, new_cost
            probes_false_positive = True
            what_probes_missed = [
                "Readiness stayed green while requests shifted onto a degraded failover path.",
                "User-facing latency increased even after reachability recovered.",
            ]
        else:
            path_recovery_status = "failed"

    elif name == "blackhole":
        broken_hop = "auth ingress"
        topo.set_link_state("api", "auth", False)
        topo.set_link_state("router-a", "auth", False)
        topo.set_link_state("router-b", "auth", False)
        timeline.append(_evt(1, "blackhole", "auth ingress disconnected"))
        new_path, new_cost = topo.shortest_path("edge", "downstream")
        if new_path is None:
            unreachable_window_seconds = 18.0
            degraded_path_requests_total = 25
            path_recovery_status = "unreachable"
            final_path, final_cost = None, float("inf")
            timeline.append(_evt(2, "unreachable", "No end-to-end path to downstream"))
            probes_false_positive = True
            what_probes_missed = [
                "Service health appeared normal before user-facing reachability collapsed.",
                "Dependency path was broken even though individual services could still appear alive.",
            ]
        else:
            final_path, final_cost = new_path, new_cost

    elif name == "asymmetric_path":
        broken_hop = "edge<->router-a cost inflation"
        topo.set_link_weight("edge", "router-a", 5.0)
        topo.set_link_weight("edge", "router-b", 1.0)
        timeline.append(_evt(1, "weight_change", "edge-router-a 1.0 -> 5.0"))
        new_path, new_cost = topo.shortest_path("edge", "downstream")
        if new_path is not None and new_path != baseline_path:
            path_changes_total = 1
            degraded_path_requests_total = 9
            convergence_seconds = 1.7
            path_recovery_status = "rerouted"
            reroute_detail = {"old_path": baseline_path, "new_path": new_path}
            timeline.append(_evt(2, "reroute", f"{baseline_path} -> {new_path}"))
            final_path, final_cost = new_path, new_cost
            probes_false_positive = True
            what_probes_missed = [
                "Requests still served, but the new path introduced material latency drift.",
            ]

    elif name == "link_flap":
        broken_hop = "router-a<->api flap"
        for i in range(3):
            topo.set_link_state("router-a", "api", False)
            timeline.append(_evt(1 + i * 2, "link_down", broken_hop))
            topo.set_link_state("router-a", "api", True)
            timeline.append(_evt(2 + i * 2, "link_up", broken_hop))
        final_path, final_cost = topo.shortest_path("edge", "downstream")
        path_changes_total = 6
        degraded_path_requests_total = 18
        convergence_seconds = 6.0
        path_recovery_status = "flapping_then_stable"
        reroute_detail = {"old_path": baseline_path, "new_path": final_path}
        probes_false_positive = True
        what_probes_missed = [
            "Readiness stayed green during route churn.",
            "Intermittent instability degraded requests without a clean outage signal.",
        ]

    else:
        raise ValueError(f"Unsupported topology decision scenario: {name}")

    success = final_path is not None
    availability_pct = 0.0 if not success else (92.0 if final_path != baseline_path or degraded_path_requests_total else 100.0)
    p50_ms = 120.0 if final_path == baseline_path else (220.0 if success else 0.0)
    p95_ms = 240.0 if final_path == baseline_path else (540.0 if success else 0.0)
    p99_ms = 420.0 if final_path == baseline_path else (880.0 if success else 0.0)
    error_rate = 0.0 if final_path == baseline_path else (0.02 if success else 0.18)
    path_extra_latency_ms = 0.0 if (not success or final_path == baseline_path) else max(0.0, (final_cost - baseline_cost) * 80.0)

    slo_met = availability_pct >= 99.5 and p99_ms <= 900.0 and (error_rate * 100.0) <= 1.0
    safe_to_operate = success and slo_met and not probes_false_positive
    recommendation = (
        "continue" if safe_to_operate
        else ("reroute" if success and final_path != baseline_path else "block")
    )

    decision = _decision_artifact(
        scenario=name,
        probes_healthy=bool(probes_false_positive or success),
        slo_met=slo_met,
        safe_to_operate=safe_to_operate,
        what_probes_missed=what_probes_missed,
        recommendation=recommendation,
    )

    ended = started + timedelta(seconds=max(1, int(convergence_seconds) + 1))

    return {
        "run_id": uuid.uuid4().hex,
        "scenario": name,
        "pod_name": "topology-lab",
        "namespace": "default",
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "success": success,
        "status": "pass" if success else "fail",
        "recovery_window_seconds": convergence_seconds if success else unreachable_window_seconds,
        "restart_count": 0,
        "probe_mismatch": probes_false_positive,
        "latency_p50_ms": p50_ms,
        "latency_p95_ms": p95_ms,
        "latency_p99_ms": p99_ms,
        "error_rate": error_rate,
        "baseline_latency_p50_ms": 120.0,
        "baseline_latency_p95_ms": 240.0,
        "baseline_latency_p99_ms": 420.0,
        "baseline_error_rate": 0.0,
        "observed_latency_p50_ms": p50_ms,
        "observed_latency_p95_ms": p95_ms,
        "observed_latency_p99_ms": p99_ms,
        "observed_error_rate": error_rate,
        "latency_p50_drift_pct": 0.0 if p50_ms == 0.0 else round(((p50_ms - 120.0) / 120.0) * 100.0, 2),
        "latency_p95_drift_pct": 0.0 if p95_ms == 0.0 else round(((p95_ms - 240.0) / 240.0) * 100.0, 2),
        "latency_p99_drift_pct": 0.0 if p99_ms == 0.0 else round(((p99_ms - 420.0) / 420.0) * 100.0, 2),
        "error_rate_delta": round(error_rate - 0.0, 4),
        "availability_achieved_pct_simulated": availability_pct,
        "baseline_path": baseline_path,
        "baseline_path_cost": baseline_cost,
        "final_path": final_path,
        "final_path_cost": None if final_path is None else final_cost,
        "path_change_timeline": timeline,
        "broken_hop": broken_hop,
        "reroute_detail": reroute_detail,
        "partial_recovery": bool(success and final_path != baseline_path),
        "convergence_seconds": convergence_seconds,
        "path_changes_total": path_changes_total,
        "unreachable_windows_total": int(unreachable_window_seconds > 0),
        "unreachable_window_seconds": unreachable_window_seconds,
        "degraded_path_requests_total": degraded_path_requests_total,
        "path_recovery_status": path_recovery_status,
        "path_extra_latency_ms": path_extra_latency_ms,
        "readiness_before": "ready",
        "readiness_after": "ready-but-degraded" if probes_false_positive and success else ("not-ready" if not success else "ready"),
        "readiness_false_positive": probes_false_positive,
        "cross_zone_degradation_pct": 0.0 if final_path == baseline_path else 18.0,
        "path_recovery_time_seconds": convergence_seconds,
        "network_availability_gap_pct": round(max(0.0, 100.0 - availability_pct), 2),
        "pass_fail_reason": (
            "Topology converged onto a degraded alternate path." if success and final_path != baseline_path
            else ("Topology remained healthy." if success else "Downstream path unreachable after link event.")
        ),
        "recommendation": (
            "Continue" if safe_to_operate
            else ("Reroute to alternate stable path." if success else "Block rollout and restore broken path.")
        ),
        "decision_artifact": decision,
        "probes_say_healthy": decision["probes_say_healthy"],
        "safe_to_operate": decision["safe_to_operate"],
        "what_probes_missed": decision["what_probes_missed"],
        "recommendation_action": decision["recommendation_action"],
        "release_decision": decision["recommendation_action"],
        "reason": "probe false positive + degraded path behavior",
        "stdout": f"Simulated topology scenario: {name}",
        "stderr": "",
        "error": None,
    }
