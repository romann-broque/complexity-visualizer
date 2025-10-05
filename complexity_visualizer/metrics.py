"""Metrics computation for dependency graphs.

This module calculates various software metrics including:
- Fan-in/Fan-out: Number of incoming/outgoing dependencies
- Instability: Ratio of efferent to total coupling (Ce / (Ce + Ca))
- Strongly Connected Components: Circular dependency detection via Tarjan's algorithm
"""
from __future__ import annotations
from typing import Dict, List, Sequence, Tuple, TypedDict

from .models import GraphSnapshot

# Type aliases for clarity
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
        """Compute all metrics for a dependency graph.
        
        Args:
            graph: The graph to analyze
            
        Returns:
            Dictionary containing all computed metrics
            
        Raises:
            ValueError: If the graph has no nodes
        """
        if not graph.nodes:
            raise ValueError("Graph has no nodes")

        node_index = graph.create_node_index()
        node_count = len(graph.nodes)

        adjacency_list = MetricsCalculator._build_adjacency_list(
            node_count, graph, node_index
        )

        fan_out, fan_in = MetricsCalculator._calculate_degrees(adjacency_list)
        instability_values = MetricsCalculator._calculate_instability(fan_out, fan_in)
        strongly_connected = MetricsCalculator._find_strongly_connected_components(
            adjacency_list
        )

        return {
            "nodeCount": node_count,
            "edgeCount": len(graph.edges),
            "fanOut": fan_out,
            "fanIn": fan_in,
            "instability": instability_values,
            "scc": strongly_connected,
        }

    @staticmethod
    def build_dependency_structure_matrix(graph: GraphSnapshot) -> Dict[str, object]:
        """Build a Dependency Structure Matrix (DSM) from the graph.
        
        A DSM is a square matrix where M[i][j] represents the number of
        dependencies from node i to node j.
        
        Args:
            graph: The graph to convert
            
        Returns:
            Dictionary with 'order' (node IDs) and 'matrix' (2D list)
            
        Raises:
            ValueError: If the graph has no nodes
        """
        if not graph.nodes:
            raise ValueError("Graph has no nodes")

        node_index = graph.create_node_index()
        node_count = len(graph.nodes)

        # Initialize matrix with zeros
        matrix = [[0] * node_count for _ in range(node_count)]

        # Fill matrix with edge weights
        for edge in graph.edges:
            source_idx = node_index.get(edge.from_id)
            target_idx = node_index.get(edge.to_id)

            if source_idx is not None and target_idx is not None:
                matrix[source_idx][target_idx] += max(1, edge.weight)

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
        """Build adjacency list representation from edges.
        
        Args:
            node_count: Number of nodes in the graph
            graph: The graph containing edges
            node_index: Mapping from node IDs to indices
            
        Returns:
            List where adjacency_list[i] contains indices of nodes that i points to
        """
        adjacency_list: AdjacencyList = [[] for _ in range(node_count)]

        for edge in graph.edges:
            source_idx = node_index.get(edge.from_id)
            target_idx = node_index.get(edge.to_id)

            if source_idx is not None and target_idx is not None:
                adjacency_list[source_idx].append(target_idx)

        return adjacency_list

    @staticmethod
    def _calculate_degrees(adjacency_list: AdjacencyList) -> Tuple[List[int], List[int]]:
        """Calculate out-degree and in-degree for each node.
        
        Out-degree (fan-out): Number of dependencies this node has
        In-degree (fan-in): Number of nodes that depend on this node
        
        Args:
            adjacency_list: Graph represented as adjacency list
            
        Returns:
            Tuple of (out_degrees, in_degrees)
        """
        node_count = len(adjacency_list)
        out_degrees = [0] * node_count
        in_degrees = [0] * node_count

        for node_idx, neighbors in enumerate(adjacency_list):
            out_degrees[node_idx] = len(neighbors)
            for neighbor_idx in neighbors:
                in_degrees[neighbor_idx] += 1

        return out_degrees, in_degrees

    @staticmethod
    def _calculate_instability(
            out_degrees: Sequence[int],
            in_degrees: Sequence[int],
    ) -> List[float]:
        """Calculate instability metric for each node.
        
        Instability = Ce / (Ce + Ca) where:
        - Ce (Efferent Coupling) = fan-out = out-degree
        - Ca (Afferent Coupling) = fan-in = in-degree
        
        Instability ranges from 0 (stable, only depended upon) to 1 (unstable, only depends on others).
        
        Args:
            out_degrees: Fan-out values for each node
            in_degrees: Fan-in values for each node
            
        Returns:
            List of instability values, rounded to 3 decimal places
        """
        instability_values: List[float] = []

        for efferent, afferent in zip(out_degrees, in_degrees):
            total_coupling = efferent + afferent

            if total_coupling == 0:
                instability = 0.0
            else:
                instability = efferent / total_coupling

            instability_values.append(round(instability, 3))

        return instability_values

    @staticmethod
    def _find_strongly_connected_components(adjacency_list: AdjacencyList) -> List[List[int]]:
        """Find strongly connected components using Tarjan's algorithm.
        
        A strongly connected component is a maximal set of nodes where
        every node is reachable from every other node. In dependency graphs,
        these represent circular dependencies.
        
        Args:
            adjacency_list: Graph represented as adjacency list
            
        Returns:
            List of components, where each component is a list of node indices
        """
        node_count = len(adjacency_list)
        current_index = 0
        stack: List[int] = []
        on_stack = [False] * node_count
        node_ids = [-1] * node_count
        low_link = [0] * node_count
        components: List[List[int]] = []

        def strongconnect(node: int) -> None:
            """Recursive DFS for Tarjan's algorithm."""
            nonlocal current_index

            node_ids[node] = low_link[node] = current_index
            current_index += 1
            stack.append(node)
            on_stack[node] = True

            # Explore neighbors
            for neighbor in adjacency_list[node]:
                if node_ids[neighbor] == -1:
                    # Neighbor not yet visited
                    strongconnect(neighbor)
                    low_link[node] = min(low_link[node], low_link[neighbor])
                elif on_stack[neighbor]:
                    # Neighbor is in current SCC
                    low_link[node] = min(low_link[node], node_ids[neighbor])

            # If node is a root node, pop the stack to form SCC
            if low_link[node] == node_ids[node]:
                component: List[int] = []
                while True:
                    popped = stack.pop()
                    on_stack[popped] = False
                    component.append(popped)
                    if popped == node:
                        break
                components.append(component)

        # Find all SCCs
        for node in range(node_count):
            if node_ids[node] == -1:
                strongconnect(node)

        return components


# Convenience functions for backward compatibility
def compute_metrics(graph: GraphSnapshot) -> MetricsReport:
    """Compute all metrics for a dependency graph."""
    return MetricsCalculator.compute_metrics(graph)


def build_dsm(graph: GraphSnapshot) -> Dict[str, object]:
    """Build a Dependency Structure Matrix from the graph."""
    return MetricsCalculator.build_dependency_structure_matrix(graph)