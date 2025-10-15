"""Compute graph metrics: fan-in/out, SCCs."""
from typing import Dict, List

from .models import Graph


def compute_metrics(graph: Graph) -> Dict:
    """Calculate all metrics for the graph."""
    if not graph.nodes:
        raise ValueError("Empty graph")

    n = len(graph.nodes)
    idx = graph.node_index()

    # Build adjacency list
    adj = [[] for _ in range(n)]
    for e in graph.edges:
        if (s := idx.get(e.from_id)) is not None and (t := idx.get(e.to_id)) is not None:
            adj[s].append(t)

    fan_out, fan_in = _degrees(adj)
    sccs = _tarjan_scc(adj)
    change_cost = _change_cost(fan_in, fan_out, sccs)

    return {
        "nodeCount": n,
        "edgeCount": len(graph.edges),
        "fanOut": fan_out,
        "fanIn": fan_in,
        "scc": sccs,
        "changeCost": change_cost
    }


def _degrees(adj: List[List[int]]) -> tuple[List[int], List[int]]:
    n = len(adj)
    out_deg = [len(neighbors) for neighbors in adj]
    in_deg = [0] * n
    for neighbors in adj:
        for v in neighbors:
            in_deg[v] += 1
    return out_deg, in_deg


def _tarjan_scc(adj: List[List[int]]) -> List[List[int]]:
    """Tarjan's algorithm for strongly connected components."""
    n = len(adj)
    index = 0
    stack = []
    on_stack = [False] * n
    indices = [-1] * n
    lowlink = [0] * n
    sccs = []

    def visit(v: int):
        nonlocal index
        indices[v] = lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack[v] = True

        for w in adj[v]:
            if indices[w] == -1:
                visit(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack[w]:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in range(n):
        if indices[v] == -1:
            visit(v)

    return sccs


def _change_cost(fan_in: List[int], fan_out: List[int], sccs: List[List[int]]) -> List[float]:
    """
    Calculate change cost: difficulty to test/refactor safely.

    Formula: changeCost = (fanOut² × fanIn) + cyclePenalty

    Why fanOut² (quadratic)?
    - Testing complexity grows exponentially with dependencies
    - Each dependency can interact with others (combinatorial explosion)
    - Mocking/setup effort is non-linear

    Why fanOut × fanIn (not fanIn²)?
    - High fanIn + low fanOut = stable component (interfaces, DTOs) → LOW cost ✅
    - Low fanIn + high fanOut = god object / service locator → HIGH cost ❌
    - Both high = central hub in bad architecture → VERY HIGH cost 🔥

    Cycle penalty: +100 per cycle member (breaks clean architecture)

    Examples:
    - Interface (fanIn=20, fanOut=0): cost = 0 (green, stable)
    - DTO (fanIn=15, fanOut=2): cost = 60 (green, simple)
    - God Object (fanIn=5, fanOut=30): cost = 4500 (red, nightmare)
    - Cyclic God Object: cost = 4600 (dark red, abandon hope)
    """
    n = len(fan_in)

    # Detect cycles
    in_cycle = [False] * n
    cycle_sizes = [0] * n
    for scc in sccs:
        if len(scc) > 1:
            for node_idx in scc:
                in_cycle[node_idx] = True
                cycle_sizes[node_idx] = len(scc)

    change_cost = []
    for i in range(n):
        # Core formula: dependencies are the real problem
        coupling_cost = fan_out[i] * (fan_in[i] ** 2)

        # Cycle penalty: breaks layered architecture
        cycle_penalty = 100 * cycle_sizes[i] if in_cycle[i] else 0

        change_cost.append(coupling_cost + cycle_penalty)

    return change_cost