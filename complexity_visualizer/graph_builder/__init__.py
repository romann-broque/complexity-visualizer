"""Graph Builder Module

Parses dependency sources and generates standardized graph.json format.
Source-agnostic output compatible with any visualization tool.
"""
from __future__ import annotations

from .build_graph import Graph, build_graph
from .models import Graph, Node, Edge

__all__ = ["Graph", "build_graph", "Node", "Edge"]
__version__ = "1.0.0"
