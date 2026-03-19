"""Base classes for metric calculation system.

This module provides the foundation for a pluggable metric system where
each metric is an independent calculator that can be added or removed
without affecting other metrics.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ..models import Graph


@dataclass
class MetricContext:
    """Shared context for metric calculation.

    This context is passed to all metric calculators and provides:
    - The dependency graph
    - Pre-computed adjacency list (for performance)
    - Node index mapping (for fast lookups)
    - Cache for storing previously computed metric results
    - Optional source metrics (complexity, loc, is_abstract)
    """

    graph: Graph
    adjacency_list: List[List[int]]
    node_index: Dict[str, int]
    n_nodes: int
    cache: Dict[str, Any] = field(default_factory=dict)
    source_metrics: Optional[Dict[str, Dict]] = None


class MetricCalculator(ABC):
    """Base class for metric calculators.

    Each metric is implemented as a separate calculator class that inherits
    from this base. This allows for:
    - Easy addition/removal of metrics
    - Clear dependencies between metrics
    - Independent testing
    - Automatic dependency resolution via topological sorting
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique metric identifier (e.g., 'fanIn', 'cycleParticipation')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the metric."""
        pass

    @property
    def dependencies(self) -> Set[str]:
        """Names of other metrics this one depends on.

        Used for dependency resolution and topological sorting.
        Example: distanceFromMainSequence depends on ['abstractness', 'instability']

        Returns:
            Set of metric names that must be computed before this one
        """
        return set()

    @property
    def export_to_codecharta(self) -> bool:
        """Whether this metric should be exported to CodeCharta format.

        Returns:
            True if the metric should appear in CodeCharta visualization
        """
        return True

    @property
    def codecharta_type(self) -> str:
        """CodeCharta attribute type.

        Returns:
            One of: 'absolute', 'relative', or 'ordinal'
        """
        return "absolute"

    @abstractmethod
    def calculate(self, context: MetricContext) -> List[Any]:
        """Calculate metric values for all nodes.

        Args:
            context: Shared context with graph, adjacency list, and cache

        Returns:
            List of metric values (one per node, same order as graph.nodes)
        """
        pass

    def validate(self, values: List[Any], context: MetricContext) -> bool:
        """Validate calculated values.

        Default implementation checks that the number of values matches
        the number of nodes. Override for custom validation logic.

        Args:
            values: Calculated metric values
            context: Metric context

        Returns:
            True if values are valid, False otherwise
        """
        return len(values) == context.n_nodes
