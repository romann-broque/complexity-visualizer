"""Core Module

Core graph building, metrics computation, and data models.
"""

from __future__ import annotations

from .metric_computation import compute_metrics
from .models import Graph, Node, Edge
from .parsers import parse_dot_directory

__all__ = ["compute_metrics", "Graph", "Node", "Edge", "parse_dot_directory"]
