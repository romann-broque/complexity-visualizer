from dataclasses import dataclass, field
from typing import List, Dict, Literal

NodeType = Literal["class", "package"]

@dataclass(frozen=True, slots=True)
class Node:
    id: str
    name: str = ""
    type: NodeType = "class"
    metrics: Dict[str, float] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class Edge:
    from_id: str
    to_id: str
    kind: str = "import"
    weight: int = 1

@dataclass(slots=True)
class GraphSnapshot:
    """Représente un graphe au temps T (sortie parser)."""
    nodes: List[Node]
    edges: List[Edge]
    meta: Dict[str, str] = field(default_factory=dict)

    def node_index(self) -> Dict[str, int]:
        return {n.id: i for i, n in enumerate(self.nodes)}