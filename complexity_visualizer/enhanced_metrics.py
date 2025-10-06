"""Enhanced metrics computation for dependency analysis.

This module extends the basic metrics with advanced coupling,
complexity, and refactoring difficulty indicators.
"""
from __future__ import annotations
from typing import Dict, List, Set, Tuple
from collections import defaultdict

from .models import GraphSnapshot
from .metrics import MetricsCalculator


class EnhancedMetrics:
    """Advanced metrics for dependency graph analysis."""

    @staticmethod
    def compute_enhanced_metrics(
            graph: GraphSnapshot,
            base_metrics: Dict,
    ) -> Dict[str, object]:
        """Compute comprehensive metrics for refactoring and coupling analysis.

        Args:
            graph: The dependency graph
            base_metrics: Basic metrics from MetricsCalculator

        Returns:
            Dictionary with enhanced metrics
        """
        node_index = graph.create_node_index()
        node_count = len(graph.nodes)

        # Extract base metrics
        fan_out = base_metrics["fanOut"]
        fan_in = base_metrics["fanIn"]
        scc = base_metrics["scc"]

        # Compute enhanced metrics
        coupling_metrics = EnhancedMetrics._compute_coupling_metrics(
            graph, fan_out, fan_in, node_count
        )

        cycle_metrics = EnhancedMetrics._compute_cycle_metrics(scc, node_count)

        architectural_metrics = EnhancedMetrics._compute_architectural_metrics(
            graph, fan_out, fan_in, node_index
        )

        refactoring_metrics = EnhancedMetrics._compute_refactoring_metrics(
            graph, scc, fan_out, fan_in, node_index
        )

        # Combine all metrics
        return {
            **base_metrics,
            "coupling": coupling_metrics,
            "cycles": cycle_metrics,
            "architecture": architectural_metrics,
            "refactoring": refactoring_metrics,
        }

    @staticmethod
    def _compute_coupling_metrics(
            graph: GraphSnapshot,
            fan_out: List[int],
            fan_in: List[int],
            node_count: int,
    ) -> Dict[str, float]:
        """Analyze coupling strength and distribution."""
        if node_count == 0:
            return {
                "averageFanOut": 0.0,
                "averageFanIn": 0.0,
                "maxFanOut": 0,
                "maxFanIn": 0,
                "couplingConcentration": 0.0,
                "bidirectionalDependencies": 0,
                "hubNodeCount": 0,
            }

        avg_fan_out = sum(fan_out) / node_count
        avg_fan_in = sum(fan_in) / node_count
        max_fan_out = max(fan_out) if fan_out else 0
        max_fan_in = max(fan_in) if fan_in else 0

        # Coupling concentration: what % of edges involve top 10% nodes
        total_coupling = [fan_out[i] + fan_in[i] for i in range(node_count)]
        sorted_coupling = sorted(total_coupling, reverse=True)
        top_10_percent_count = max(1, node_count // 10)
        top_10_percent_coupling = sum(sorted_coupling[:top_10_percent_count])
        total_edges = sum(total_coupling)

        coupling_concentration = (
            top_10_percent_coupling / total_edges if total_edges > 0 else 0.0
        )

        # Bidirectional dependencies
        bidirectional = EnhancedMetrics._count_bidirectional_deps(graph)

        # Hub nodes (nodes with high coupling)
        threshold = 10
        hub_count = sum(1 for coupling in total_coupling if coupling >= threshold)

        return {
            "averageFanOut": round(avg_fan_out, 2),
            "averageFanIn": round(avg_fan_in, 2),
            "maxFanOut": max_fan_out,
            "maxFanIn": max_fan_in,
            "couplingConcentration": round(coupling_concentration, 3),
            "bidirectionalDependencies": bidirectional,
            "hubNodeCount": hub_count,
        }

    @staticmethod
    def _count_bidirectional_deps(graph: GraphSnapshot) -> int:
        """Count pairs of nodes with mutual dependencies (A→B and B→A)."""
        edge_set = {(edge.from_id, edge.to_id) for edge in graph.edges}
        bidirectional_count = 0

        for edge in graph.edges:
            reverse_edge = (edge.to_id, edge.from_id)
            if reverse_edge in edge_set and edge.from_id < edge.to_id:
                # Count each pair only once
                bidirectional_count += 1

        return bidirectional_count

    @staticmethod
    def _compute_cycle_metrics(
            scc: List[List[int]],
            node_count: int,
    ) -> Dict[str, object]:
        """Analyze circular dependency patterns."""
        # Filter out trivial SCCs (single nodes)
        cycles = [component for component in scc if len(component) > 1]

        if not cycles:
            return {
                "cycleCount": 0,
                "nodesInCycles": 0,
                "percentageInCycles": 0.0,
                "largestCycleSize": 0,
                "averageCycleSize": 0.0,
                "tangleScore": 0,
            }

        cycle_sizes = [len(cycle) for cycle in cycles]
        nodes_in_cycles = sum(cycle_sizes)

        # Tangle score: sum of (size - 1) for each cycle
        # Represents minimum edges to break to eliminate all cycles
        tangle_score = sum(size - 1 for size in cycle_sizes)

        return {
            "cycleCount": len(cycles),
            "nodesInCycles": nodes_in_cycles,
            "percentageInCycles": round(100 * nodes_in_cycles / node_count, 2),
            "largestCycleSize": max(cycle_sizes),
            "averageCycleSize": round(sum(cycle_sizes) / len(cycles), 2),
            "tangleScore": tangle_score,
        }

    @staticmethod
    def _compute_architectural_metrics(
            graph: GraphSnapshot,
            fan_out: List[int],
            fan_in: List[int],
            node_index: Dict[str, int],
    ) -> Dict[str, object]:
        """Analyze architectural properties."""
        node_count = len(graph.nodes)

        if node_count == 0:
            return {
                "leafNodeCount": 0,
                "rootNodeCount": 0,
                "isolatedNodeCount": 0,
                "layerability": 0.0,
                "unresolvedRatio": 0.0,
            }

        # Node types
        leaf_nodes = sum(1 for fo in fan_out if fo == 0)
        root_nodes = sum(1 for fi in fan_in if fi == 0)
        isolated_nodes = sum(
            1 for i in range(node_count)
            if fan_out[i] == 0 and fan_in[i] == 0
        )

        # Layerability: how well the graph can be organized in layers
        # Approximated by ratio of (root + leaf) nodes
        layerable_nodes = leaf_nodes + root_nodes - isolated_nodes
        layerability = layerable_nodes / node_count if node_count > 0 else 0.0

        # Unresolved dependency ratio
        unresolved_ids = set(graph.meta.get("unresolvedIds", []))
        unresolved_ratio = len(unresolved_ids) / node_count

        return {
            "leafNodeCount": leaf_nodes,
            "rootNodeCount": root_nodes,
            "isolatedNodeCount": isolated_nodes,
            "layerability": round(layerability, 3),
            "unresolvedRatio": round(unresolved_ratio, 3),
        }

    @staticmethod
    def _compute_refactoring_metrics(
            graph: GraphSnapshot,
            scc: List[List[int]],
            fan_out: List[int],
            fan_in: List[int],
            node_index: Dict[str, int],
    ) -> Dict[str, object]:
        """Compute metrics indicating refactoring difficulty."""
        node_count = len(graph.nodes)

        # Average transitive dependencies (propagation cost)
        transitive_deps = EnhancedMetrics._compute_transitive_deps(
            graph, node_index
        )
        avg_transitive = (
            sum(transitive_deps) / node_count if node_count > 0 else 0.0
        )
        max_transitive = max(transitive_deps) if transitive_deps else 0

        # Breaking point nodes (nodes that break cycles when removed)
        breaking_points = EnhancedMetrics._identify_breaking_points(
            graph, scc, node_index
        )

        # Change impact: nodes with high transitive dependencies
        high_impact_threshold = max(10, node_count // 10)
        high_impact_nodes = sum(
            1 for td in transitive_deps if td >= high_impact_threshold
        )

        # Refactoring difficulty score (0-100)
        # Based on cycles, coupling, and transitive dependencies
        cycles = [c for c in scc if len(c) > 1]
        cycle_penalty = min(50, len(cycles) * 5)
        coupling_penalty = min(30, (sum(fan_out) / node_count) * 2)
        transitive_penalty = min(20, (avg_transitive / node_count) * 100)

        difficulty_score = cycle_penalty + coupling_penalty + transitive_penalty

        return {
            "averageTransitiveDeps": round(avg_transitive, 2),
            "maxTransitiveDeps": max_transitive,
            "breakingPointNodes": len(breaking_points),
            "highImpactNodes": high_impact_nodes,
            "difficultyScore": round(difficulty_score, 1),
        }

    @staticmethod
    def _compute_transitive_deps(
            graph: GraphSnapshot,
            node_index: Dict[str, int],
    ) -> List[int]:
        """Compute transitive closure for each node (all reachable nodes)."""
        node_count = len(graph.nodes)

        # Build adjacency list
        adjacency: List[Set[int]] = [set() for _ in range(node_count)]
        for edge in graph.edges:
            src_idx = node_index.get(edge.from_id)
            tgt_idx = node_index.get(edge.to_id)
            if src_idx is not None and tgt_idx is not None:
                adjacency[src_idx].add(tgt_idx)

        # Compute transitive closure using DFS
        transitive_counts = []
        for start_node in range(node_count):
            visited = set()
            stack = [start_node]

            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)

                for neighbor in adjacency[node]:
                    if neighbor not in visited:
                        stack.append(neighbor)

            # Subtract 1 to exclude the node itself
            transitive_counts.append(len(visited) - 1)

        return transitive_counts

    @staticmethod
    def _identify_breaking_points(
            graph: GraphSnapshot,
            scc: List[List[int]],
            node_index: Dict[str, int],
    ) -> Set[int]:
        """Identify nodes whose removal would break circular dependencies."""
        cycles = [component for component in scc if len(component) > 1]

        if not cycles:
            return set()

        # Build adjacency for cycle analysis
        node_count = len(graph.nodes)
        adjacency: List[Set[int]] = [set() for _ in range(node_count)]

        for edge in graph.edges:
            src_idx = node_index.get(edge.from_id)
            tgt_idx = node_index.get(edge.to_id)
            if src_idx is not None and tgt_idx is not None:
                adjacency[src_idx].add(tgt_idx)

        breaking_points: Set[int] = set()

        # For each cycle, find nodes that connect to other cycles or outside
        for cycle in cycles:
            cycle_set = set(cycle)
            for node in cycle:
                # Check if node has connections outside the cycle
                external_connections = (
                        len(adjacency[node] - cycle_set) > 0
                )
                if external_connections:
                    breaking_points.add(node)

        return breaking_points