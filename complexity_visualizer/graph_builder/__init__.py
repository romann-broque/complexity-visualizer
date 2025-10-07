"""Graph Builder Module

Parses dependency sources and generates standardized graph.json format.
Source-agnostic output compatible with any visualization tool.
"""
from __future__ import annotations

from .build_graph import GraphBuilder, build_graph
from .models import GraphSnapshot, Node, Edge

__all__ = ["GraphBuilder", "build_graph", "GraphSnapshot", "Node", "Edge"]
__version__ = "1.0.0"
