"""Metric calculators for fan-in and fan-out (degree metrics)."""

from typing import List

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
