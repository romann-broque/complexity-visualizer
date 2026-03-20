"""Metric calculators for fan-in and fan-out (degree metrics)."""

from typing import List, Set

from ..algorithms import compute_in_degrees, compute_out_degrees
from ..base import MetricCalculator, MetricContext


class FanOutCalculator(MetricCalculator):
    """Calculator for fan-out metric.

    Fan-out measures the number of direct outgoing dependencies.
    High fan-out indicates a class that depends on many others.
    """

    @property
    def name(self) -> str:
        return "fanOut"

    @property
    def description(self) -> str:
        return "Number of direct outgoing dependencies"

    def calculate(self, context: MetricContext) -> List[int]:
        return compute_out_degrees(context.adjacency_list)


class FanInCalculator(MetricCalculator):
    """Calculator for fan-in metric.

    Fan-in measures how many classes depend on this class.
    High fan-in means many clients - changes can have wide impact.
    """

    @property
    def name(self) -> str:
        return "fanIn"

    @property
    def description(self) -> str:
        return "Number of classes depending on this class"

    def calculate(self, context: MetricContext) -> List[int]:
        return compute_in_degrees(context.adjacency_list)


class HubScoreCalculator(MetricCalculator):
    """Calculator for hub score metric.

    Hub score identifies God classes by detecting classes that are both
    heavily depended upon (high fanIn) AND depend on many things (high fanOut).

    Formula: hubScore = fanIn × fanOut

    Why this works:
    - High fanIn alone = shared interface (fine)
    - High fanOut alone = orchestrator (fine)
    - Both high = bottleneck (God class - dangerous)

    A class with hubScore > 0 only when BOTH fanIn and fanOut are non-zero.
    The multiplication amplifies only classes that sit at crossroads of the
    dependency graph.
    """

    @property
    def name(self) -> str:
        return "hubScore"

    @property
    def description(self) -> str:
        return "God class detector: fanIn × fanOut (high = bottleneck)"

    @property
    def dependencies(self) -> Set[str]:
        return {"fanIn", "fanOut"}

    def calculate(self, context: MetricContext) -> List[int]:
        fan_in = context.cache["fanIn"]
        fan_out = context.cache["fanOut"]

        return [fan_in[i] * fan_out[i] for i in range(context.n_nodes)]
