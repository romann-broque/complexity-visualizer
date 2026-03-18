"""Metric calculator for stability analysis (Robert C. Martin)."""

from typing import List, Set

from ..base import MetricCalculator, MetricContext


class InstabilityCalculator(MetricCalculator):
    """Calculator for instability metric (Robert C. Martin).

    Formula: I = fanOut / (fanIn + fanOut)

    Interpretation:
    - I = 0.0: Maximally stable (many dependents, few dependencies)
               Typical for: Domain entities, core abstractions
    - I = 1.0: Maximally unstable (few dependents, many dependencies)
               Typical for: Controllers, orchestrators, infrastructure

    Used to detect Clean Architecture violations:
    - Domain layer should have I ≈ 0 (stable, no outgoing dependencies)
    - Application layer should have I ≈ 0.3-0.5
    - Infrastructure layer should have I ≈ 1 (unstable, depends on everything)

    High instability in domain layer = architectural violation!
    """

    @property
    def name(self) -> str:
        return "instability"

    @property
    def description(self) -> str:
        return "Instability metric (fanOut / (fanIn + fanOut))"

    @property
    def dependencies(self) -> Set[str]:
        return {"fanIn", "fanOut"}

    @property
    def codecharta_type(self) -> str:
        return "relative"

    def calculate(self, context: MetricContext) -> List[float]:
        fan_in = context.cache["fanIn"]
        fan_out = context.cache["fanOut"]

        instability = []
        for fi, fo in zip(fan_in, fan_out):
            total = fi + fo
            instability.append(fo / total if total > 0 else 0.0)

        return instability
