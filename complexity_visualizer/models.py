"""Domain models for the complexity visualizer.

This module defines the core data structures representing:
- Nodes: Java classes or packages in the dependency graph
- Edges: Dependencies between nodes
- GraphSnapshot: A complete dependency graph at a point in time
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal

NodeType = Literal["class", "package"]


@dataclass(frozen=True, slots=True)
class Node:
    """Represents a node in the dependency graph (typically a Java class)."""

    id: str
    name: str = ""
    type: NodeType = "class"
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Edge:
    """Represents a directed dependency between two nodes."""

    from_id: str
    to_id: str
    kind: str = "import"
    weight: int = 1


@dataclass(slots=True)
class GraphSnapshot:
    """Immutable snapshot of a dependency graph at a specific point in time.

    This represents the complete state of dependencies parsed from DOT files,
    including metadata about the source and any unresolved dependencies.
    """

    nodes: List[Node]
    edges: List[Edge]
    meta: Dict[str, str] = field(default_factory=dict)

    def create_node_index(self) -> Dict[str, int]:
        """Create a mapping from node ID to its index position.

        Returns:
            Dictionary mapping node IDs to their list indices for O(1) lookups.
        """
        return {node.id: index for index, node in enumerate(self.nodes)}