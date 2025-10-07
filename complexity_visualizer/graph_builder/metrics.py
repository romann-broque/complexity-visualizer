"""Metrics computation for dependency graphs.

Calculates:
- Fan-in/Fan-out
- Instability (Ce / (Ce + Ca))
- Strongly Connected Components (Tarjan's algorithm)
"""
from __future__ import annotations
from typing import Dict, List, Sequence, Tuple, TypedDict

from .models import GraphSnapshot

AdjacencyList = List[List[int]]
NodeIndex = Dict[str, int]


class MetricsReport(TypedDict):
    """Comprehensive metrics for a dependency graph."""
    nodeCount: int
    edgeCount: int
    fanOut: List[int]
    fanIn: List[int]
    instability: List[float]
    scc: List[List[int]]


class MetricsCalculator:
    """Calculator for dependency graph metrics."""

    @staticmethod
    def compute_metrics(graph: GraphSnapshot) -> MetricsReport:
        """Compute all metrics for a dependency graph."""
        if not graph.nodes:
            raise ValueError("Graph has no nodes")

        node_index = graph.create_node_index()
        node_count = len(graph.nodes)

        adjacency = MetricsCalculator._build_adjacency_list(
            node_count, graph, node_index
        )

        fan_out, fan_in = MetricsCalculator._calculate_degrees(adjacency)
        instability = MetricsCalculator._calculate_instability(fan_out, fan_in)
        scc = MetricsCalculator._find_strongly_connected_components(adjacency)

        return {
            "nodeCount": node_count,
            "edgeCount": len(graph.edges),
            "fanOut": fan_out,
            "fanIn": fan_in,
            "instability": instability,
            "scc": scc,
        }

    @staticmethod
    def build_dependency_structure_matrix(graph: GraphSnapshot) -> Dict[str, object]:
        """Build DSM where M[i][j] = dependencies from i to j."""
        if not graph.nodes:
            raise ValueError("Graph has no nodes")

        node_index = graph.create_node_index()
        n = len(graph.nodes)
        matrix = [[0] * n for _ in range(n)]

        for edge in graph.edges:
            src = node_index.get(edge.from_id)
            tgt = node_index.get(edge.to_id)
            if src is not None and tgt is not None:
                matrix[src][tgt] += max(1, edge.weight)

        return {
            "order": [node.id for node in graph.nodes],
            "matrix": matrix,
        }

    @staticmethod
    def _build_adjacency_list(
            node_count: int,
            graph: GraphSnapshot,
            node_index: NodeIndex,
    ) -> AdjacencyList:
        """Build adjacency list from edges."""
        adj: AdjacencyList = [[] for _ in range(node_count)]
        for edge in graph.edges:
            src = node_index.get(edge.from_id)
            tgt = node_index.get(edge.to_id)
            if src is not None and tgt is not None:
                adj[src].append(tgt)
        return adj

    @staticmethod
    def _calculate_degrees(adj: AdjacencyList) -> Tuple[List[int], List[int]]:
        """Calculate out-degree (fan-out) and in-degree (fan-in)."""
        n = len(adj)
        out_deg = [0] * n
        in_deg = [0] * n

        for node, neighbors in enumerate(adj):
            out_deg[node] = len(neighbors)
            for neighbor in neighbors:
                in_deg[neighbor] += 1

        return out_deg, in_deg

    @staticmethod
    def _calculate_instability(
            out_deg: Sequence[int],
            in_deg: Sequence[int],
    ) -> List[float]:
        """Calculate instability = Ce / (Ce + Ca).

        Range: 0 (stable, only depended upon) to 1 (unstable, only depends).
        """
        result = []
        for efferent, afferent in zip(out_deg, in_deg):
            total = efferent + afferent
            instability = efferent / total if total > 0 else 0.0
            result.append(round(instability, 3))
        return result

    @staticmethod
    def _find_strongly_connected_components(adj: AdjacencyList) -> List[List[int]]:
        """Find SCCs using Tarjan's algorithm (circular dependencies)."""
        n = len(adj)
        index = 0
        stack: List[int] = []
        on_stack = [False] * n
        indices = [-1] * n
        lowlink = [0] * n
        components: List[List[int]] = []

        def strongconnect(v: int) -> None:
            nonlocal index
            indices[v] = lowlink[v] = index
            index += 1
            stack.append(v)
            on_stack[v] = True

            for w in adj[v]:
                if indices[w] == -1:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif on_stack[w]:
                    lowlink[v] = min(lowlink[v], indices[w])

            if lowlink[v] == indices[v]:
                component: List[int] = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.append(w)
                    if w == v:
                        break
                components.append(component)

        for v in range(n):
            if indices[v] == -1:
                strongconnect(v)

        return components