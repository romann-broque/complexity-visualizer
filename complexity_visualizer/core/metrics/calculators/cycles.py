"""Metric calculators for cycle detection and participation."""

from typing import List

from ..algorithms import tarjan_scc
from ..base import MetricCalculator, MetricContext


class CycleParticipationCalculator(MetricCalculator):
    """Calculator for cycle participation metric.

    For each node, returns the size of the cycle it belongs to.
    Returns 0 if the node is not part of any cycle.

    This metric is crucial for identifying strongly coupled components
    that are difficult to refactor independently.
    """

    @property
    def name(self) -> str:
        return "cycleParticipation"

    @property
    def description(self) -> str:
        return "Size of dependency cycle this class belongs to (0 if not in cycle)"

    def calculate(self, context: MetricContext) -> List[int]:
        sccs = tarjan_scc(context.adjacency_list)

        cycle_sizes = [0] * context.n_nodes
        for scc in sccs:
            if len(scc) > 1:
                for node_idx in scc:
                    cycle_sizes[node_idx] = len(scc)

        return cycle_sizes
