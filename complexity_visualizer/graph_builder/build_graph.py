from __future__ import annotations
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .models import GraphSnapshot
from .dot_parser import DotFileParser
from .graph_filter import GraphFilter
from .metrics import MetricsCalculator
from .enhanced_metrics import EnhancedMetrics
from .node_formatter import NodeFormatter
from .io_utils import FileWriter


class GraphBuilder:
    """Orchestrates graph building from DOT files."""

    @staticmethod
    def build_graph(
            dot_directory: str,
            output_graph_path: str,
            output_dsm_path: Optional[str] = None,
            include_prefixes: Optional[List[str]] = None,
            enhanced: bool = True,
    ) -> Dict[str, object]:
        """Parse DOT files, compute metrics, write graph.json.

        Args:
            dot_directory: Path to .dot files
            output_graph_path: Where to write graph.json
            output_dsm_path: Optional DSM.json output
            include_prefixes: Optional package filters
            enhanced: Compute enhanced metrics (default: True)

        Returns:
            Dict with nodeCount, edgeCount, paths, and key metrics
        """
        FileWriter.ensure_parent_directory(output_graph_path)
        if output_dsm_path:
            FileWriter.ensure_parent_directory(output_dsm_path)

        # Parse DOT files
        snapshot = DotFileParser.parse_directory(dot_directory)
        snapshot.meta.setdefault(
            "generatedAt",
            datetime.now(timezone.utc).isoformat()
        )

        # Apply prefix filter
        if include_prefixes:
            snapshot = GraphFilter.filter_by_prefixes(snapshot, include_prefixes)

        # Compute metrics
        base_metrics = MetricsCalculator.compute_metrics(snapshot)
        if enhanced:
            metrics = EnhancedMetrics.compute_enhanced_metrics(snapshot, base_metrics)
        else:
            metrics = base_metrics

        # Build and write graph.json
        graph_payload = GraphBuilder._build_graph_payload(snapshot, metrics)
        FileWriter.write_json(output_graph_path, graph_payload)

        # Optionally write DSM
        dsm_output_path = None
        if output_dsm_path:
            dsm_data = MetricsCalculator.build_dependency_structure_matrix(snapshot)
            FileWriter.write_json(output_dsm_path, dsm_data)
            dsm_output_path = output_dsm_path

        return {
            "nodeCount": metrics["nodeCount"],
            "edgeCount": metrics["edgeCount"],
            "graphPath": output_graph_path,
            "dsmPath": dsm_output_path,
            "metrics": {
                "difficultyScore": metrics.get("refactoring", {}).get("difficultyScore", 0),
                "cycleCount": metrics.get("cycles", {}).get("cycleCount", 0),
                "tangleScore": metrics.get("cycles", {}).get("tangleScore", 0),
            }
        }

    @staticmethod
    def _build_graph_payload(
            snapshot: GraphSnapshot,
            metrics: Dict[str, object],
    ) -> Dict[str, object]:
        """Construct complete graph.json payload."""
        formatted_nodes = NodeFormatter.format_nodes_with_metrics(snapshot, metrics)

        metrics_with_order = {
            **metrics,
            "order": [node.id for node in snapshot.nodes],
        }

        return {
            "meta": snapshot.meta,
            "nodes": formatted_nodes,
            "edges": [asdict(edge) for edge in snapshot.edges],
            "metrics": metrics_with_order,
        }


# Convenience function
def build_graph(
        dot_directory: str,
        output_graph_path: str,
        output_dsm_path: Optional[str] = None,
        include_prefixes: Optional[List[str]] = None,
        enhanced: bool = True,
) -> Dict[str, object]:
    """Build dependency graph from DOT files."""
    return GraphBuilder.build_graph(
        dot_directory,
        output_graph_path,
        output_dsm_path,
        include_prefixes,
        enhanced,
    )