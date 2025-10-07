"""Enhanced metrics for advanced dependency analysis.

Extends basic metrics with:
- Coupling analysis (concentration, bidirectional deps, hub nodes)
- Cycle analysis (tangle score, cycle distribution)
- Architectural metrics (layerability, leaf/root nodes)
- Refactoring metrics (transitive deps, breaking points, difficulty score)
"""
from __future__ import annotations
from typing import Dict, List, Set

from .models import GraphSnapshot


class EnhancedMetrics:
    """Advanced metrics for dependency analysis."""

    @staticmethod
    def compute_enhanced_metrics(
            graph: GraphSnapshot,
            base_metrics: Dict,
    ) -> Dict[str, object]:
        """Compute comprehensive enhanced metrics."""
        node_index = graph.create_node_index()
        node_count = len(graph.nodes)

        fan_out = base_metrics["fanOut"]
        fan_in = base_metrics["fanIn"]
        scc = base_metrics["scc"]

        coupling = EnhancedMetrics._compute_coupling_metrics(
            graph, fan_out, fan_in, node_count
        )
        cycles = EnhancedMetrics._compute_cycle_metrics(scc, node_count)
        architecture = EnhancedMetrics._compute_architectural_metrics(
            graph, fan_out, fan_in, node_index
        )
        refactoring = EnhancedMetrics._compute_refactoring_metrics(
            graph, scc, fan_out, fan_in, node_index
        )

        return {
            **base_metrics,
            "coupling": coupling,
            "cycles": cycles,
            "architecture": architecture,
            "refactoring": refactoring,
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

        total_coupling = [fan_out[i] + fan_in[i] for i in range(node_count)]
        sorted_coupling = sorted(total_coupling, reverse=True)

        top_10_pct = max(1, node_count // 10)
        concentration = (
            sum(sorted_coupling[:top_10_pct]) / sum(total_coupling)
            if sum(total_coupling) > 0 else 0.0
        )

        bidirectional = EnhancedMetrics._count_bidirectional(graph)
        hub_count = sum(1 for c in total_coupling if c >= 10)

        return {
            "averageFanOut": round(sum(fan_out) / node_count, 2),
            "averageFanIn": round(sum(fan_in) / node_count, 2),
            "maxFanOut": max(fan_out) if fan_out else 0,
            "maxFanIn": max(fan_in) if fan_in else 0,
            "couplingConcentration": round(concentration, 3),
            "bidirectionalDependencies": bidirectional,
            "hubNodeCount": hub_count,
        }

    @staticmethod
    def _count_bidirectional(graph: GraphSnapshot) -> int:
        """Count mutual dependencies (A→B and B→A)."""
        edges = {(e.from_id, e.to_id) for e in graph.edges}
        count = 0
        for e in graph.edges:
            if (e.to_id, e.from_id) in edges and e.from_id < e.to_id:
                count += 1
        return count

    @staticmethod
    def _compute_cycle_metrics(
            scc: List[List[int]],
            node_count: int,
    ) -> Dict[str, object]:
        """Analyze circular dependency patterns."""
        cycles = [c for c in scc if len(c) > 1]

        if not cycles:
            return {
                "cycleCount": 0,
                "nodesInCycles": 0,
                "percentageInCycles": 0.0,
                "largestCycleSize": 0,
                "averageCycleSize": 0.0,
                "tangleScore": 0,
            }

        sizes = [len(c) for c in cycles]
        nodes_in_cycles = sum(sizes)
        tangle_score = sum(s - 1 for s in sizes)

        return {
            "cycleCount": len(cycles),
            "nodesInCycles": nodes_in_cycles,
            "percentageInCycles": round(100 * nodes_in_cycles / node_count, 2),
            "largestCycleSize": max(sizes),
            "averageCycleSize": round(sum(sizes) / len(cycles), 2),
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
        n = len(graph.nodes)
        if n == 0:
            return {
                "leafNodeCount": 0,
                "rootNodeCount": 0,
                "isolatedNodeCount": 0,
                "layerability": 0.0,
                "unresolvedRatio": 0.0,
            }

        leaf = sum(1 for fo in fan_out if fo == 0)
        root = sum(1 for fi in fan_in if fi == 0)
        isolated = sum(1 for i in range(n) if fan_out[i] == 0 and fan_in[i] == 0)

        layerable = leaf + root - isolated
        layerability = layerable / n if n > 0 else 0.0

        unresolved = set(graph.meta.get("unresolvedIds", []))
        unresolved_ratio = len(unresolved) / n

        return {
            "leafNodeCount": leaf,
            "rootNodeCount": root,
            "isolatedNodeCount": isolated,
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
        """Compute refactoring difficulty metrics."""
        n = len(graph.nodes)

        transitive = EnhancedMetrics._compute_transitive_deps(graph, node_index)
        avg_transitive = sum(transitive) / n if n > 0 else 0.0
        max_transitive = max(transitive) if transitive else 0

        breaking_points = EnhancedMetrics._identify_breaking_points(
            graph, scc, node_index
        )

        high_impact_threshold = max(10, n // 10)
        high_impact = sum(1 for t in transitive if t >= high_impact_threshold)

        # Difficulty score (0-100)
        cycles = [c for c in scc if len(c) > 1]
        cycle_penalty = min(50, len(cycles) * 5)
        coupling_penalty = min(30, (sum(fan_out) / n) * 2) if n > 0 else 0
        transitive_penalty = min(20, (avg_transitive / n) * 100) if n > 0 else 0
        difficulty = cycle_penalty + coupling_penalty + transitive_penalty

        return {
            "averageTransitiveDeps": round(avg_transitive, 2),
            "maxTransitiveDeps": max_transitive,
            "breakingPointNodes": len(breaking_points),
            "highImpactNodes": high_impact,
            "difficultyScore": round(difficulty, 1),
        }

    @staticmethod
    def _compute_transitive_deps(
            graph: GraphSnapshot,
            node_index: Dict[str, int],
    ) -> List[int]:
        """Compute transitive closure (all reachable nodes) for each node."""
        n = len(graph.nodes)
        adj: List[Set[int]] = [set() for _ in range(n)]

        for edge in graph.edges:
            src = node_index.get(edge.from_id)
            tgt = node_index.get(edge.to_id)
            if src is not None and tgt is not None:
                adj[src].add(tgt)

        counts = []
        for start in range(n):
            visited = set()
            stack = [start]

            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)

                for neighbor in adj[node]:
                    if neighbor not in visited:
                        stack.append(neighbor)

            counts.append(len(visited) - 1)  # Exclude self

        return counts

    @staticmethod
    def _identify_breaking_points(
            graph: GraphSnapshot,
            scc: List[List[int]],
            node_index: Dict[str, int],
    ) -> Set[int]:
        """Identify nodes whose removal breaks cycles."""
        cycles = [c for c in scc if len(c) > 1]
        if not cycles:
            return set()

        n = len(graph.nodes)
        adj: List[Set[int]] = [set() for _ in range(n)]

        for edge in graph.edges:
            src = node_index.get(edge.from_id)
            tgt = node_index.get(edge.to_id)
            if src is not None and tgt is not None:
                adj[src].add(tgt)

        breaking: Set[int] = set()
        for cycle in cycles:
            cycle_set = set(cycle)
            for node in cycle:
                # Nodes with external connections are breaking points
                if len(adj[node] - cycle_set) > 0:
                    breaking.add(node)

        return breaking