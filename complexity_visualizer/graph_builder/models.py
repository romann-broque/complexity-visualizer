"""Core data models for dependency graphs."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True, slots=True)
class Node:
    id: str
    type: str = "class"


@dataclass(frozen=True, slots=True)
class Edge:
    from_id: str
    to_id: str
    weight: int = 1


@dataclass
class Graph:
    nodes: List[Node]
    edges: List[Edge]
    meta: Dict = field(default_factory=dict)

    def node_index(self) -> Dict[str, int]:
        return {n.id: i for i, n in enumerate(self.nodes)}