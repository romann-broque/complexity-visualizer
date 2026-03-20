"""Core data models for dependency graphs."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Node:
    id: str
    type: str = "class"


@dataclass(frozen=True)
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


# Extended models for intermediate JSON format


@dataclass
class NodeMetrics:
    """Metrics for a single node/class."""

    fanIn: int
    fanOut: int
    transitiveDeps: int
    complexity: int
    loc: int
    cycleParticipation: int = 0
    bidirectionalLinks: int = 0
    crossPackageDeps: int = 0
    instability: float = 0.0
    hubScore: int = 0


@dataclass
class NodeWithMetrics:
    """Node with its computed metrics."""

    id: str
    name: str
    type: str
    package: str
    metrics: NodeMetrics


@dataclass
class Cycle:
    """Strongly connected component (dependency cycle)."""

    id: int
    nodes: List[str]
    size: int


@dataclass
class Summary:
    """Aggregated summary statistics."""

    totalClasses: int
    totalEdges: int
    avgComplexity: float
    avgFanOut: float
    cycleCount: int


@dataclass
class Hotspots:
    """Lists of problematic classes."""

    highComplexity: List[str]
    highFanOut: List[str]
    highBurden: List[str]


@dataclass
class Aggregates:
    """Aggregated analysis results."""

    summary: Summary
    cycles: List[Cycle]
    hotspots: Hotspots


@dataclass
class PackageStats:
    """Statistics for a package."""

    classCount: int
    avgComplexity: float
    totalLoc: int


@dataclass
class IntermediateFormat:
    """Complete intermediate JSON format."""

    meta: Dict
    nodes: List[NodeWithMetrics]
    edges: List[Edge]
    aggregates: Aggregates
    packages: Dict[str, PackageStats]
