"""Metric calculators for cycle detection and participation."""

from typing import List

from ..algorithms import tarjan_scc
from ..base import MetricCalculator, MetricContext
from ..utils import is_class_node


class CycleParticipationCalculator(MetricCalculator):
    """Calculator for cycle participation metric.

    For each node, returns the size of the cycle it belongs to.
    Returns 0 if the node is not part of any cycle.

    This metric is crucial for identifying strongly coupled components
    that are difficult to refactor independently.

    Note: This calculator only considers cycles between classes, not packages.
    Package nodes are filtered out before cycle detection.
    """

    @property
    def name(self) -> str:
        return "cycleParticipation"

    @property
    def description(self) -> str:
        return "Size of dependency cycle this class belongs to (0 if not in cycle)"

    def calculate(self, context: MetricContext) -> List[int]:
        # Build class-only adjacency list and mapping
        class_indices = []
        original_to_class = {}  # Maps original index to class-only index

        for i, node in enumerate(context.graph.nodes):
            if is_class_node(node.id):
                original_to_class[i] = len(class_indices)
                class_indices.append(i)

        # Build adjacency list for classes only
        n_classes = len(class_indices)
        class_adj = [[] for _ in range(n_classes)]

        for i, original_idx in enumerate(class_indices):
            for neighbor_idx in context.adjacency_list[original_idx]:
                # Only include edges to other classes
                if neighbor_idx in original_to_class:
                    class_neighbor_idx = original_to_class[neighbor_idx]
                    class_adj[i].append(class_neighbor_idx)

        # Run SCC detection on class-only graph
        sccs = tarjan_scc(class_adj)

        # Map results back to original indices (packages get 0)
        cycle_sizes = [0] * context.n_nodes
        for scc in sccs:
            if len(scc) > 1:  # Ignore self-loops
                for class_idx in scc:
                    original_idx = class_indices[class_idx]
                    cycle_sizes[original_idx] = len(scc)

        return cycle_sizes
