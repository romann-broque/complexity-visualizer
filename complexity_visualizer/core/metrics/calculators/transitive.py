"""Metric calculator for transitive dependencies."""

from typing import List

from ..algorithms import transitive_closure
from ..base import MetricCalculator, MetricContext


class TransitiveDepsCalculator(MetricCalculator):
    """Calculator for transitive dependencies metric.

    Measures the total number of classes reachable through the dependency chain.
    This is the "blast radius" - how many classes are potentially affected
    by changes to the dependencies of this class.
    """

    @property
    def name(self) -> str:
        return "transitiveDeps"

    @property
    def description(self) -> str:
        return "Total reachable classes through dependency chain (blast radius)"

    def calculate(self, context: MetricContext) -> List[int]:
        transitive = []
        for start in range(context.n_nodes):
            reachable = transitive_closure(context.adjacency_list, start)
            transitive.append(len(reachable))
        return transitive
