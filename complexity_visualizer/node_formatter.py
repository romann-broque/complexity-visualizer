"""Node formatting for JSON output.

This module handles the conversion of internal node representations
to the output format expected by visualization tools.
"""
from __future__ import annotations
from typing import Dict, List, Set

from .models import GraphSnapshot
from .metrics import MetricsReport


class NodeFormatter:
    """Formats nodes for JSON serialization."""

    @staticmethod
    def format_nodes_with_metrics(
            snapshot: GraphSnapshot,
            metrics: MetricsReport,
    ) -> List[Dict[str, object]]:
        """Format nodes with their computed metrics for output.

        Args:
            snapshot: Graph containing the nodes
            metrics: Computed metrics for all nodes

        Returns:
            List of dictionaries ready for JSON serialization
        """
        fan_out_values: List[int] = metrics["fanOut"]
        fan_in_values: List[int] = metrics["fanIn"]
        instability_values: List[float] = metrics["instability"]

        unresolved_node_ids: Set[str] = set(
            snapshot.meta.get("unresolvedIds", [])
        )

        formatted_nodes: List[Dict[str, object]] = []

        for index, node in enumerate(snapshot.nodes):
            node_dict = {
                "id": node.id,
                "type": node.type,
                "name": NodeFormatter._extract_simple_class_name(node.id),
                "unresolved": node.id in unresolved_node_ids,
                "metrics": {
                    "fanOut": fan_out_values[index],
                    "fanIn": fan_in_values[index],
                    "stability": 1 - instability_values[index],
                },
            }
            formatted_nodes.append(node_dict)

        return formatted_nodes

    @staticmethod
    def _extract_simple_class_name(fully_qualified_name: str) -> str:
        """Extract simple class name from fully qualified class name.

        Handles both slash and dot separators, and converts inner class
        markers ($) to dots for readability.

        Args:
            fully_qualified_name: e.g., "com/example/Foo" or "com.example.Bar$Inner"

        Returns:
            Simple class name, e.g., "Foo" or "Bar.Inner"

        Examples:
            >>> _extract_simple_class_name("com.example.MyClass")
            'MyClass'
            >>> _extract_simple_class_name("com/example/Outer$Inner")
            'Outer.Inner'
        """
        # Handle slash separators first
        after_slash = fully_qualified_name.rsplit("/", 1)[-1]

        # Then handle dot separators
        if "." in after_slash:
            simple_name = after_slash.rsplit(".", 1)[-1]
        else:
            simple_name = after_slash

        # Convert inner class markers to dots for readability
        return simple_name.replace("$", ".")