"""Metric registry with automatic dependency resolution.

The registry manages all available metric calculators and ensures
they are computed in the correct order based on their dependencies.
"""

from typing import Dict, List, Optional, Type

from .base import MetricCalculator, MetricContext


class MetricRegistry:
    """Central registry for all available metrics.

    Handles:
    - Metric registration
    - Dependency resolution via topological sorting
    - Coordinated computation of all metrics
    """

    def __init__(self):
        self._calculators: Dict[str, MetricCalculator] = {}

    def register(self, calculator_class: Type[MetricCalculator]) -> None:
        """Register a metric calculator.

        Args:
            calculator_class: Class (not instance) of MetricCalculator
        """
        calculator = calculator_class()
        self._calculators[calculator.name] = calculator

    def get(self, name: str) -> Optional[MetricCalculator]:
        """Get calculator by name.

        Args:
            name: Metric name

        Returns:
            MetricCalculator instance or None if not found
        """
        return self._calculators.get(name)

    def list_all(self) -> List[str]:
        """List all registered metric names.

        Returns:
            List of metric names
        """
        return list(self._calculators.keys())

    def compute_all(self, context: MetricContext) -> Dict[str, List]:
        """Compute all registered metrics in dependency order.

        Uses topological sorting to ensure dependencies are computed
        before dependent metrics.

        Args:
            context: Shared metric context

        Returns:
            Dict mapping metric name to list of values

        Raises:
            ValueError: If circular dependency detected or unknown dependency
        """
        ordered = self._topological_sort()

        results = {}
        for name in ordered:
            calculator = self._calculators[name]

            values = calculator.calculate(context)

            if not calculator.validate(values, context):
                raise ValueError(f"Metric {name} produced invalid values")

            results[name] = values
            context.cache[name] = values

        return results

    def _topological_sort(self) -> List[str]:
        """Sort metrics by dependencies using Kahn's algorithm.

        Ensures dependencies are computed before dependent metrics.

        Returns:
            List of metric names in topologically sorted order

        Raises:
            ValueError: If circular dependency detected or unknown dependency
        """
        in_degree = {name: 0 for name in self._calculators}
        graph = {name: [] for name in self._calculators}

        for name, calc in self._calculators.items():
            for dep in calc.dependencies:
                if dep not in self._calculators:
                    raise ValueError(
                        f"Metric '{name}' depends on unknown metric '{dep}'"
                    )
                graph[dep].append(name)
                in_degree[name] += 1

        queue = [name for name, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self._calculators):
            raise ValueError("Circular dependency detected in metrics")

        return result


_registry = MetricRegistry()


def get_registry() -> MetricRegistry:
    """Get the global metric registry instance.

    Returns:
        Global MetricRegistry instance
    """
    return _registry
