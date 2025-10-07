from __future__ import annotations
from typing import Dict, List, Set

from .models import GraphSnapshot


class NodeFormatter:
    """Formats nodes for JSON serialization."""

    @staticmethod
    def format_nodes_with_metrics(
            snapshot: GraphSnapshot,
            metrics: Dict,
    ) -> List[Dict[str, object]]:
        """Format nodes with computed metrics for output."""
        fan_out = metrics["fanOut"]
        fan_in = metrics["fanIn"]
        instability = metrics["instability"]
        unresolved_ids = set(snapshot.meta.get("unresolvedIds", []))

        formatted = []
        for idx, node in enumerate(snapshot.nodes):
            formatted.append({
                "id": node.id,
                "type": node.type,
                "name": NodeFormatter._extract_simple_name(node.id),
                "unresolved": node.id in unresolved_ids,
                "metrics": {
                    "fanOut": fan_out[idx],
                    "fanIn": fan_in[idx],
                    "stability": 1 - instability[idx],
                },
            })
        return formatted

    @staticmethod
    def _extract_simple_name(fqn: str) -> str:
        """Extract simple name from fully qualified name.

        Examples:
            'com.example.Foo' -> 'Foo'
            'com/example/Bar$Inner' -> 'Bar.Inner'
        """
        after_slash = fqn.rsplit("/", 1)[-1]
        simple = after_slash.rsplit(".", 1)[-1] if "." in after_slash else after_slash
        return simple.replace("$", ".")