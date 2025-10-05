from __future__ import annotations
from typing import Dict, List, Sequence, Tuple, TypedDict
from .models import GraphSnapshot

class MetricsReport(TypedDict):
    nodeCount: int
    edgeCount: int
    fanOut: List[int]
    fanIn: List[int]
    instability: List[float]
    scc: List[List[int]]

AdjacencyList = List[List[int]]

# ---------- API principale (fonctions pures) ----------

def compute_metrics(graph: GraphSnapshot) -> MetricsReport:
    _ensure_nodes(graph)
    index = graph.node_index()
    n = len(graph.nodes)
    adj = _build_adjacency(n, graph, index)
    out_deg, in_deg = _degrees(adj)
    instability = _instability(out_deg, in_deg)
    scc = _tarjan(adj)
    return {
        "nodeCount": n,
        "edgeCount": len(graph.edges),
        "fanOut": out_deg,
        "fanIn": in_deg,
        "instability": instability,
        "scc": scc,
    }

def build_dsm(graph: GraphSnapshot) -> Dict[str, object]:
    _ensure_nodes(graph)
    index = graph.node_index()
    n = len(graph.nodes)
    M = [[0]*n for _ in range(n)]
    for e in graph.edges:
        i = index.get(e.from_id); j = index.get(e.to_id)
        if i is None or j is None:
            continue
        M[i][j] += max(1, int(e.weight))
    return {"order": [n.id for n in graph.nodes], "matrix": M}

# ---------- Helpers pures ----------

def _ensure_nodes(graph: GraphSnapshot) -> None:
    if not graph.nodes:
        raise ValueError("Graph has no nodes")

def _build_adjacency(n: int, graph: GraphSnapshot, index: Dict[str, int]) -> AdjacencyList:
    adj: AdjacencyList = [[] for _ in range(n)]
    for e in graph.edges:
        i = index.get(e.from_id); j = index.get(e.to_id)
        if i is None or j is None:
            continue
        adj[i].append(j)
    return adj

def _degrees(adj: AdjacencyList) -> Tuple[List[int], List[int]]:
    n = len(adj)
    out_deg = [0]*n
    in_deg  = [0]*n
    for i, nbrs in enumerate(adj):
        out_deg[i] = len(nbrs)
        for j in nbrs:
            in_deg[j] += 1
    return out_deg, in_deg

def _instability(out_deg: Sequence[int], in_deg: Sequence[int]) -> List[float]:
    res: List[float] = []
    for ce, ca in zip(out_deg, in_deg):
        total = ce + ca
        res.append(round((ce / total) if total else 0.0, 3))
    return res

def _tarjan(adj: AdjacencyList) -> List[List[int]]:
    n = len(adj)
    idx = 0
    stack: List[int] = []
    on_stack = [False]*n
    ids = [-1]*n
    low = [0]*n
    comps: List[List[int]] = []

    def dfs(v: int) -> None:
        nonlocal idx
        ids[v] = low[v] = idx; idx += 1
        stack.append(v); on_stack[v] = True
        for w in adj[v]:
            if ids[w] == -1:
                dfs(w); low[v] = min(low[v], low[w])
            elif on_stack[w]:
                low[v] = min(low[v], ids[w])
        if low[v] == ids[v]:
            comp: List[int] = []
            while True:
                w = stack.pop(); on_stack[w] = False
                comp.append(w)
                if w == v: break
            comps.append(comp)

    for v in range(n):
        if ids[v] == -1:
            dfs(v)
    return comps
