"""Metric calculators for coupling analysis."""

from typing import List

from ..base import MetricCalculator, MetricContext


class BidirectionalLinksCalculator(MetricCalculator):
    """Calculator for bidirectional dependencies metric.

    Counts how many classes have mutual dependencies with this class
    (A→B AND B→A). This is a strong indicator of tight coupling.

    Note: This excludes cycles already detected by SCC analysis, focusing
    on direct mutual dependencies.
    """

    @property
    def name(self) -> str:
        return "bidirectionalLinks"

    @property
    def description(self) -> str:
        return "Number of mutual dependencies (A→B AND B→A)"

    def calculate(self, context: MetricContext) -> List[int]:
        adj = context.adjacency_list
        bidirectional = [0] * context.n_nodes

        for i in range(context.n_nodes):
            for j in adj[i]:
                if i in adj[j]:
                    bidirectional[i] += 1

        return bidirectional


class CrossPackageDepsCalculator(MetricCalculator):
    """Calculator for cross-package dependencies metric.

    Counts how many different packages this class depends on.
    Useful for detecting bounded context violations in Clean Architecture.

    High values indicate a class that crosses package boundaries frequently,
    which may violate architectural principles.
    """

    @property
    def name(self) -> str:
        return "crossPackageDeps"

    @property
    def description(self) -> str:
        return "Number of different packages this class depends on"

    def calculate(self, context: MetricContext) -> List[int]:
        cross_package = []

        for i, node in enumerate(context.graph.nodes):
            node_package = self._extract_package(node.id)

            dep_packages = set()
            for j in context.adjacency_list[i]:
                dep_node = context.graph.nodes[j]
                dep_package = self._extract_package(dep_node.id)
                if dep_package != node_package:
                    dep_packages.add(dep_package)

            cross_package.append(len(dep_packages))

        return cross_package

    @staticmethod
    def _extract_package(fqn: str) -> str:
        """Extract package from fully qualified name.

        Args:
            fqn: Fully qualified class name (e.g., 'com.example.foo.Bar')

        Returns:
            Package name (e.g., 'com.example.foo')
        """
        parts = fqn.rsplit(".", 1)
        return parts[0] if len(parts) > 1 else ""
