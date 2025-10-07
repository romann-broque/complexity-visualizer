from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal

NodeType = Literal["class", "package"]


@dataclass(frozen=True, slots=True)
class Node:
    """Node in dependency graph (class or package)."""
    id: str
    name: str = ""
    type: NodeType = "class"
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Edge:
    """Directed dependency between nodes."""
    from_id: str
    to_id: str
    kind: str = "import"
    weight: int = 1


@dataclass(slots=True)
class GraphSnapshot:
    """Complete dependency graph snapshot."""
    nodes: List[Node]
    edges: List[Edge]
    meta: Dict[str, str] = field(default_factory=dict)

    def create_node_index(self) -> Dict[str, int]:
        """Create node ID to index mapping."""
        return {node.id: idx for idx, node in enumerate(self.nodes)}