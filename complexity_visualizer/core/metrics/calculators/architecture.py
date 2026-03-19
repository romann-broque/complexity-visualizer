"""Package-level architecture metric calculators."""

from typing import Dict, List, Set

from ..base import MetricCalculator, MetricContext


class AbstractnessCalculator(MetricCalculator):
    """Calculator for abstractness metric (package-level).

    Abstractness measures the ratio of abstract types (interfaces and abstract classes)
    to total types in a package.

    Formula: abstractness = abstract_count / total_count per package

    This is a package-level metric, but each class in the package receives
    the same abstractness value for visualization purposes.

    Requires source_metrics with 'is_abstract' field to function properly.
    If not available, returns None for all nodes.
    """

    @property
    def name(self) -> str:
        return "abstractness"

    @property
    def description(self) -> str:
        return "Ratio of interfaces and abstract classes to total classes in the package (0=concrete, 1=abstract)"

    @property
    def dependencies(self) -> Set[str]:
        return set()

    def calculate(self, context: MetricContext) -> List[float]:
        """Calculate abstractness for each node based on its package."""
        # Check if is_abstract data is available
        if context.source_metrics is None:
            # Return 0.0 for all nodes if source metrics not available
            return [0.0] * context.n_nodes

        # Type narrowing: source_metrics is not None from here on
        source_metrics = context.source_metrics

        if not any("is_abstract" in m for m in source_metrics.values()):
            # Return 0.0 if is_abstract field not present
            return [0.0] * context.n_nodes

        # Group nodes by package
        package_stats: Dict[str, Dict[str, int]] = {}

        for node in context.graph.nodes:
            # Extract package from FQN (everything before the last dot)
            fqn = node.id
            if "." in fqn:
                # Handle inner classes: Outer$Inner should use Outer's package
                if "$" in fqn:
                    fqn = fqn.split("$")[0]
                package = ".".join(fqn.split(".")[:-1])
            else:
                package = "(default)"

            if package not in package_stats:
                package_stats[package] = {"total": 0, "abstract": 0}

            src_metrics = source_metrics.get(node.id, {})
            is_abstract = src_metrics.get("is_abstract", 0)

            package_stats[package]["total"] += 1
            package_stats[package]["abstract"] += is_abstract

        # Compute abstractness per package
        package_abstractness: Dict[str, float] = {}
        for pkg, stats in package_stats.items():
            if stats["total"] > 0:
                package_abstractness[pkg] = stats["abstract"] / stats["total"]
            else:
                package_abstractness[pkg] = 0.0

        # Assign package-level abstractness to each node
        result = []
        for node in context.graph.nodes:
            fqn = node.id
            if "." in fqn:
                if "$" in fqn:
                    fqn = fqn.split("$")[0]
                package = ".".join(fqn.split(".")[:-1])
            else:
                package = "(default)"

            result.append(package_abstractness.get(package, 0.0))

        return result


class DistanceFromMainSequenceCalculator(MetricCalculator):
    """Calculator for distance from main sequence metric.

    The main sequence is the ideal balance between abstractness and instability
    as defined by Robert C. Martin in "Clean Architecture".

    Formula: distance = |abstractness + instability - 1|

    - distance = 0: Balanced (ideal)
    - distance = 1: Problematic (either Zone of Pain or Zone of Uselessness)

    Zones:
    - Zone of Pain: High instability + Low abstractness (concrete but unstable)
    - Zone of Uselessness: Low instability + High abstractness (abstract but unused)
    """

    @property
    def name(self) -> str:
        return "distanceFromMainSequence"

    @property
    def description(self) -> str:
        return "Distance from the ideal balance of abstractness and stability (0=balanced, 1=problematic)"

    @property
    def dependencies(self) -> Set[str]:
        return {"abstractness", "instability"}

    def calculate(self, context: MetricContext) -> List[float]:
        """Calculate distance from main sequence for each node."""
        abstractness = context.cache["abstractness"]
        instability = context.cache["instability"]

        distances = []
        for i in range(context.n_nodes):
            a = abstractness[i]
            i_val = instability[i]
            distance = abs(a + i_val - 1.0)
            distances.append(distance)

        return distances
