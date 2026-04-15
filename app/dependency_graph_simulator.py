from __future__ import annotations
from typing import Dict, Any, List

_DEFAULT_GRAPH = {
    "edge": ["api"],
    "api": ["auth", "catalog"],
    "auth": ["postgres"],
    "catalog": ["redis"],
    "postgres": [],
    "redis": [],
}

def simulate_dependency_impact(
    source_node: str,
    failure_mode: str,
    graph: dict[str, list[str]] | None = None,
) -> Dict[str, Any]:
    g = graph or _DEFAULT_GRAPH
    impacted: List[str] = []
    stack = [source_node]
    seen = set()

    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        impacted.append(node)
        for parent, deps in g.items():
            if node in deps and parent not in seen:
                stack.append(parent)

    return {
        "dependency_graph": g,
        "dependency_root": source_node,
        "failure_mode": failure_mode,
        "impacted_services": impacted,
        "blast_radius_size": len(impacted),
        "dependency_edges": [
            {"source": src, "target": dst, "protocol": "http" if dst != "postgres" else "tcp"}
            for src, dsts in g.items()
            for dst in dsts
        ],
    }
