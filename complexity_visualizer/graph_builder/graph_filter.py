from __future__ import annotations
from typing import Iterable, Set, Tuple

from .models import GraphSnapshot


class GraphFilter:
    """Filters for dependency graphs."""

    @staticmethod
    def filter_by_prefixes(
            snapshot: GraphSnapshot,
            include_prefixes: Iterable[str],
    ) -> GraphSnapshot:
        """Keep only nodes with IDs starting with given prefixes.

        Filters nodes and edges, updates metadata accordingly.
        """
        prefix_tuples: Tuple[str, ...] = tuple(include_prefixes)
        if not prefix_tuples:
            return snapshot

        # Keep matching nodes
        kept_ids: Set[str] = {
            node.id for node in snapshot.nodes
            if any(node.id.startswith(p) for p in prefix_tuples)
        }

        filtered_nodes = [n for n in snapshot.nodes if n.id in kept_ids]
        filtered_edges = [
            e for e in snapshot.edges
            if e.from_id in kept_ids and e.to_id in kept_ids
        ]

        # Update metadata
        updated_meta = dict(snapshot.meta)
        if "unresolvedIds" in updated_meta:
            updated_meta["unresolvedIds"] = [
                nid for nid in updated_meta["unresolvedIds"]
                if nid in kept_ids
            ]

        return GraphSnapshot(
            nodes=filtered_nodes,
            edges=filtered_edges,
            meta=updated_meta,
        )