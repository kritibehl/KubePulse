import heapq

GRAPH = {
    "client": {"edge": 1, "backup": 5},
    "edge": {"client": 1, "api": 2},
    "backup": {"client": 5, "api": 1},
    "api": {"edge": 2, "backup": 1, "db": 3},
    "db": {"api": 3},
}

def shortest_path(graph, start, end, failed_link=None):
    queue = [(0, start, [])]
    visited = set()

    while queue:
        cost, node, path = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]

        if node == end:
            return {"path": path, "cost": cost}

        for neighbor, weight in graph.get(node, {}).items():
            if failed_link and {node, neighbor} == set(failed_link):
                continue
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))

    return {"path": [], "cost": None, "status": "unreachable"}

if __name__ == "__main__":
    print("normal:", shortest_path(GRAPH, "client", "db"))
    print("edge-api failed:", shortest_path(GRAPH, "client", "db", failed_link=("edge", "api")))
