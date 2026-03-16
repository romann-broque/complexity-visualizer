"""Compute graph metrics: fan-in/out, SCCs, complexity."""

from typing import Dict, List, Optional

from .models import Graph


def compute_metrics(
    graph: Graph, source_metrics: Optional[Dict[str, Dict]] = None
) -> Dict:
    """Calculate all metrics for the graph."""
    if not graph.nodes:
        raise ValueError("Empty graph")

    n = len(graph.nodes)
    idx = graph.node_index()

    # Build adjacency list
    adj = [[] for _ in range(n)]
    for e in graph.edges:
        if (s := idx.get(e.from_id)) is not None and (
            t := idx.get(e.to_id)
        ) is not None:
            adj[s].append(t)

    fan_out, fan_in = _degrees(adj)
    sccs = _tarjan_scc(adj)
    transitive_deps = _transitive_dependencies(adj)

    # Extract source code metrics if provided
    complexity_list = []
    loc_list = []
    methods_list = []

    if source_metrics:
        for node in graph.nodes:
            metrics = source_metrics.get(node.id, {})
            complexity_list.append(metrics.get("complexity", 1))
            loc_list.append(metrics.get("loc", 0))
            methods_list.append(metrics.get("methods", 0))
    else:
        # Defaults if no source analysis
        complexity_list = [1] * n
        loc_list = [0] * n
        methods_list = [0] * n

    change_impact = _change_impact_score(fan_in, fan_out, sccs, transitive_deps)

    return {
        "nodeCount": n,
        "edgeCount": len(graph.edges),
        "fanOut": fan_out,
        "fanIn": fan_in,
        "scc": sccs,
        "transitiveDeps": transitive_deps,
        "complexity": complexity_list,
        "loc": loc_list,
        "methods": methods_list,
        "maintenanceBurden": change_impact,
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


def _transitive_dependencies(adj: List[List[int]]) -> List[int]:
    """
    Calculate transitive dependencies: total reachable nodes from each node.

    This measures the "blast radius" - how many classes are potentially
    affected by changes through the dependency chain.

    Uses BFS to count all reachable nodes (direct + indirect dependencies).
    """
    n = len(adj)
    transitive = []

    for start in range(n):
        visited = set()
        queue = [start]
        visited.add(start)

        while queue:
            node = queue.pop(0)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # Don't count the node itself
        transitive.append(len(visited) - 1)

    return transitive


def _change_impact_score(
    fan_in: List[int],
    fan_out: List[int],
    sccs: List[List[int]],
    transitive_deps: List[int],
) -> List[float]:
    """
    Calculate change impact: real-world difficulty to safely modify a class.

    Formula: changeImpact = (transitiveDeps × fanIn) + cyclePenalty²

    Why this works better:

    1. transitiveDeps = "blast radius" when you modify dependencies
       - Class with 3 direct deps but 50 transitive deps = high impact
       - Class with 10 direct deps but 10 transitive deps = medium impact

    2. fanIn = "breaking change radius"
       - How many classes directly depend on this one
       - High fanIn = must ensure backward compatibility

    3. Cycle penalty² = exponential cost
       - Cycles prevent refactoring in any direction
       - Must fix the entire cycle at once

    Examples:
    - Leaf utility (fanIn=20, transitive=0): score = 0 ✅ GREEN
    - Orchestrator (fanIn=5, transitive=10): score = 50 🟡 YELLOW
    - Deep god object (fanIn=8, transitive=80): score = 640 🔴 RED
    - Cyclic core (fanIn=10, transitive=40, cycle=5): score = 400 + 2500 = 2900 🔥 DARK RED
    """
    n = len(fan_in)

    # Detect cycles
    cycle_sizes = [0] * n
    for scc in sccs:
        if len(scc) > 1:
            for node_idx in scc:
                cycle_sizes[node_idx] = len(scc)

    impact = []
    for i in range(n):
        # Core: blast radius × breaking change risk
        base_impact = transitive_deps[i] * fan_in[i]

        # Cycles are architectural showstoppers
        cycle_penalty = (cycle_sizes[i] ** 2) * 100 if cycle_sizes[i] > 0 else 0

        impact.append(base_impact + cycle_penalty)

    return impact
