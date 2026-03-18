"""Composite metric calculator for maintenance burden."""

from typing import List, Set

from ..base import MetricCalculator, MetricContext


class MaintenanceBurdenCalculator(MetricCalculator):
    """Calculator for maintenance burden metric.

    This is a composite metric that combines multiple factors to estimate
    the real-world difficulty of safely modifying a class.

    Formula: (transitiveDeps × fanIn) + cyclePenalty²

    Components:
    1. transitiveDeps × fanIn = blast radius when modifying dependencies
       combined with breaking change risk
    2. cyclePenalty² = exponential cost for being in a cycle

    Examples:
    - Leaf utility (fanIn=20, transitive=0): score = 0 (GREEN)
    - Orchestrator (fanIn=5, transitive=10): score = 50 (YELLOW)
    - Deep god object (fanIn=8, transitive=80): score = 640 (RED)
    - Cyclic core (fanIn=10, transitive=40, cycle=5): score = 2900 (DARK RED)
    """

    @property
    def name(self) -> str:
        return "maintenanceBurden"

    @property
    def description(self) -> str:
        return (
            "Change impact score combining blast radius, breaking changes, and cycles"
        )

    @property
    def dependencies(self) -> Set[str]:
        return {"fanIn", "transitiveDeps", "cycleParticipation"}

    def calculate(self, context: MetricContext) -> List[float]:
        fan_in = context.cache["fanIn"]
        transitive_deps = context.cache["transitiveDeps"]
        cycle_sizes = context.cache["cycleParticipation"]

        impact = []
        for i in range(context.n_nodes):
            base_impact = transitive_deps[i] * fan_in[i]

            cycle_penalty = (cycle_sizes[i] ** 2) * 100 if cycle_sizes[i] > 0 else 0

            impact.append(base_impact + cycle_penalty)

        return impact
