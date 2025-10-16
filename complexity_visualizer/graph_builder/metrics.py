"""Compute graph metrics: fan-in/out, SCCs, complexity."""
from typing import Dict, List, Optional, Tuple
from math import log1p

from .models import Graph

def compute_metrics(graph: Graph, source_metrics: Optional[Dict[str, Dict]] = None) -> Dict:
    """Calculate all metrics for the graph (graph + code blended)."""
    if not graph.nodes:
        raise ValueError("Empty graph")

    n = len(graph.nodes)
    idx = graph.node_index()

    # Build adjacency
    adj = [[] for _ in range(n)]
    for e in graph.edges:
        s = idx.get(e.from_id)
        t = idx.get(e.to_id)
        if s is not None and t is not None and s != t:
            adj[s].append(t)

    fan_out, fan_in = _degrees(adj)
    sccs = _tarjan_scc(adj)
    scc_size = _scc_size_per_node(n, sccs)
    transitive_deps = _transitive_dependencies(adj)

    # Code metrics (defaults if missing)
    complexity = [1] * n
    loc = [0] * n
    methods = [0] * n
    if source_metrics:
        for i, node in enumerate(graph.nodes):
            sm = source_metrics.get(node.id, {})
            complexity[i] = int(sm.get("complexity", 1))
            loc[i]        = int(sm.get("loc", 0))
            methods[i]    = int(sm.get("methods", 0))

    # Maintenance burden
    mb_raw = _maintenance_burden(
        fan_in, fan_out, transitive_deps, scc_size,
        complexity, loc, methods,
        alpha=1.0, beta=2.0, gamma=1.0
    )

    return {
        "nodeCount": n,
        "edgeCount": len(graph.edges),
        "fanOut": fan_out,
        "fanIn": fan_in,
        "scc": sccs,
        "sccSize": scc_size,
        "transitiveDeps": transitive_deps,
        "complexity": complexity,
        "loc": loc,
        "methods": methods,
        "maintenanceBurden": mb_raw,
    }

def _degrees(adj: List[List[int]]) -> Tuple[List[int], List[int]]:
    n = len(adj)
    out_deg = [len(nei) for nei in adj]
    in_deg = [0] * n
    for u in range(n):
        for v in adj[u]:
            in_deg[v] += 1
    return out_deg, in_deg

def _tarjan_scc(adj: List[List[int]]) -> List[List[int]]:
    n = len(adj)
    index = 0
    stack: List[int] = []
    on_stack = [False] * n
    ids = [-1] * n
    low = [0] * n
    comps: List[List[int]] = []

    def dfs(at: int) -> None:
        nonlocal index
        ids[at] = low[at] = index
        index += 1
        stack.append(at)
        on_stack[at] = True
        for to in adj[at]:
            if ids[to] == -1:
                dfs(to)
                low[at] = min(low[at], low[to])
            elif on_stack[to]:
                low[at] = min(low[at], ids[to])
        if low[at] == ids[at]:
            comp: List[int] = []
            while True:
                node = stack.pop()
                on_stack[node] = False
                comp.append(node)
                if node == at:
                    break
            comps.append(comp)

    for v in range(n):
        if ids[v] == -1:
            dfs(v)
    return comps

def _scc_size_per_node(n: int, sccs: List[List[int]]) -> List[int]:
    size = [1] * n
    for comp in sccs:
        if len(comp) > 1:
            for i in comp:
                size[i] = len(comp)
    return size

def _transitive_dependencies(adj: List[List[int]]) -> List[int]:
    n = len(adj)
    out = [0] * n
    for start in range(n):
        seen = {start}
        q = [start]
        while q:
            u = q.pop(0)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        out[start] = len(seen) - 1
    return out

def _maintenance_burden(
        fan_in: List[int],
        fan_out: List[int],
        transitive: List[int],
        scc_size: List[int],
        complexity: List[int],
        loc: List[int],
        methods: List[int],
        alpha: float = 1.0,
        beta: float = 2.0,
        gamma: float = 1.0,
) -> List[float]:
    """
    Blend graph coupling, blast radius, and code complexity into a single cost proxy.
    MB = α * (coupling * max(1, blast)) + β * code + γ * cyclePenalty
    where:
      coupling     = fanOut^2 + 0.5*fanIn
      blast        = transitiveDeps
      code         = complexity * log1p(loc) * (1 + 0.1*methods)
      cyclePenalty = (sccSize^2) * 100
    """
    n = len(fan_in)
    mb: List[float] = [0.0] * n
    for i in range(n):
        coupling = (fan_out[i] ** 2) + 0.5 * fan_in[i]
        blast = max(1, transitive[i])
        code = complexity[i] * log1p(loc[i]) * (1 + 0.1 * methods[i])
        cycle_penalty = (scc_size[i] ** 2) * 100 if scc_size[i] > 1 else 0
        mb[i] = alpha * (coupling * blast) + beta * code + gamma * cycle_penalty
    return mb