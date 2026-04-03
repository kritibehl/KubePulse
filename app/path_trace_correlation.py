from __future__ import annotations
from typing import Dict, List, Optional

def _pairwise(path: Optional[List[str]]) -> List[str]:
    if not path or len(path) < 2:
        return []
    return [f"{path[i]}->{path[i+1]}" for i in range(len(path) - 1)]

def _baseline_hop_latencies(path: Optional[List[str]]) -> Dict[str, float]:
    hops = _pairwise(path)
    if not hops:
        return {}
    # simple deterministic baseline model
    return {hop: 20.0 for hop in hops}

def _degraded_hop_latencies(
    baseline_path: Optional[List[str]],
    final_path: Optional[List[str]],
    broken_hop: Optional[str],
    scenario: str,
) -> Dict[str, float]:
    baseline = _baseline_hop_latencies(final_path)
    if not final_path:
        return {}

    hop_map = dict(baseline)
    final_hops = _pairwise(final_path)

    # scenario-specific latency inflation
    if scenario == "link_failure_failover":
        for hop in final_hops:
            hop_map[hop] = 35.0
        if "router-a->auth" in hop_map:
            hop_map["router-a->auth"] = 80.0

    elif scenario == "asymmetric_path":
        for hop in final_hops:
            hop_map[hop] = 30.0
        if "edge->router-b" in hop_map:
            hop_map["edge->router-b"] = 70.0

    elif scenario == "link_flap":
        for hop in final_hops:
            hop_map[hop] = 45.0

    elif scenario == "blackhole":
        for hop in final_hops:
            hop_map[hop] = 999.0

    return hop_map

def correlate_path_trace(report: dict) -> dict:
    baseline_path = report.get("baseline_path")
    final_path = report.get("final_path")
    scenario = report.get("scenario", "unknown")
    broken_hop = report.get("broken_hop")

    baseline_hops = _pairwise(baseline_path)
    final_hops = _pairwise(final_path)

    baseline_lat = _baseline_hop_latencies(baseline_path)
    final_lat = _degraded_hop_latencies(baseline_path, final_path, broken_hop, scenario)

    removed_hops = [h for h in baseline_hops if h not in final_hops]
    added_hops = [h for h in final_hops if h not in baseline_hops]

    latency_deltas = []
    for hop in final_hops:
        before = baseline_lat.get(hop, 20.0 if hop in baseline_hops else 0.0)
        after = final_lat.get(hop, before)
        latency_deltas.append({
            "hop": hop,
            "before_ms": round(before, 2),
            "after_ms": round(after, 2),
            "delta_ms": round(after - before, 2),
        })

    degraded_hop = None
    if latency_deltas:
        degraded_hop = max(latency_deltas, key=lambda x: x["delta_ms"])["hop"]

    before_after_timeline = [
        {
            "phase": "before",
            "path": baseline_path,
            "hops": baseline_hops,
            "total_estimated_path_latency_ms": round(sum(baseline_lat.values()), 2),
        },
        {
            "phase": "after",
            "path": final_path,
            "hops": final_hops,
            "total_estimated_path_latency_ms": round(sum(final_lat.values()), 2),
        },
    ]

    trace_style_events = []
    t = 0.0
    for hop in baseline_hops:
        trace_style_events.append({
            "phase": "before",
            "hop": hop,
            "start_ms": round(t, 2),
            "duration_ms": round(baseline_lat.get(hop, 20.0), 2),
        })
        t += baseline_lat.get(hop, 20.0)

    t = 0.0
    for hop in final_hops:
        trace_style_events.append({
            "phase": "after",
            "hop": hop,
            "start_ms": round(t, 2),
            "duration_ms": round(final_lat.get(hop, 20.0), 2),
        })
        t += final_lat.get(hop, 20.0)

    artifact = {
        "baseline_path": baseline_path,
        "final_path": final_path,
        "removed_hops": removed_hops,
        "added_hops": added_hops,
        "broken_hop": broken_hop,
        "degraded_hop": degraded_hop,
        "latency_deltas": latency_deltas,
        "before_after_timeline": before_after_timeline,
        "trace_style_events": trace_style_events,
        "path_shift_summary": (
            f"path shifted from {' -> '.join(baseline_path)} to {' -> '.join(final_path)}"
            if baseline_path and final_path and baseline_path != final_path
            else "no path shift"
        ),
    }

    return {
        "path_trace_correlation": artifact,
        "degraded_hop": degraded_hop,
        "path_shift_summary": artifact["path_shift_summary"],
    }
