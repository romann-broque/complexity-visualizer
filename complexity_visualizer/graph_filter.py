"""Graph filtering utilities.

This module provides functionality to filter dependency graphs based on
various criteria, such as package prefixes.
"""
from __future__ import annotations
from typing import Iterable, Set, Tuple

from .models import GraphSnapshot, Node, Edge


class GraphFilter:
    """Filters for dependency graphs."""

    @staticmethod
    def filter_by_prefixes(
            snapshot: GraphSnapshot,
            include_prefixes: Iterable[str],
    ) -> GraphSnapshot:
        """Keep only nodes whose ID starts with one of the given prefixes.

        This also filters edges to keep only those connecting retained nodes,
        and updates metadata accordingly.

        Args:
            snapshot: The graph to filter
            include_prefixes: List of package prefixes to include

        Returns:
            New GraphSnapshot with filtered nodes and edges

        Example:
            >>> filter_by_prefixes(graph, ["com.myapp", "org.myapp"])
            # Returns graph with only nodes in com.myapp.* and org.myapp.*
        """
        prefix_tuples: Tuple[str, ...] = tuple(include_prefixes)

        if not prefix_tuples:
            return snapshot

        # Identify nodes to keep
        kept_node_ids: Set[str] = {
            node.id
            for node in snapshot.nodes
            if any(node.id.startswith(prefix) for prefix in prefix_tuples)
        }

        # Filter nodes while preserving order
        filtered_nodes = [
            node for node in snapshot.nodes
            if node.id in kept_node_ids
        ]

        # Filter edges to keep only internal edges
        filtered_edges = [
            edge for edge in snapshot.edges
            if edge.from_id in kept_node_ids and edge.to_id in kept_node_ids
        ]

        # Update metadata
        updated_metadata = dict(snapshot.meta)
        if "unresolvedIds" in updated_metadata:
            updated_metadata["unresolvedIds"] = [
                node_id
                for node_id in updated_metadata["unresolvedIds"]
                if node_id in kept_node_ids
            ]

        return GraphSnapshot(
            nodes=filtered_nodes,
            edges=filtered_edges,
            meta=updated_metadata,
        )