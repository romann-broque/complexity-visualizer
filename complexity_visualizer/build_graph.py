"""Main graph building orchestration.

This module coordinates the parsing, filtering, metrics computation,
and output generation for dependency graphs.
"""
from __future__ import annotations
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .models import GraphSnapshot
from .dot_parser import DotFileParser
from .graph_filter import GraphFilter
from .metrics import MetricsCalculator
from .node_formatter import NodeFormatter
from .io_utils import FileWriter


class GraphBuilder:
    """Orchestrates the building of dependency graphs from DOT files."""

    @staticmethod
    def build_graph(
            dot_directory: str,
            output_graph_path: str,
            output_dsm_path: Optional[str] = None,
            include_prefixes: Optional[List[str]] = None,
    ) -> Dict[str, object]:
        """Parse DOT files, compute metrics, and write output files.
        
        This is the main entry point for graph building. It:
        1. Parses all DOT files in the directory
        2. Optionally filters by package prefixes
        3. Computes all metrics
        4. Writes graph.json and optionally DSM.json
        
        Args:
            dot_directory: Path to directory containing .dot files
            output_graph_path: Where to write graph.json
            output_dsm_path: Optional path for DSM.json output
            include_prefixes: Optional list of package prefixes to include
            
        Returns:
            Dictionary with build statistics and output paths
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
        # Apply prefix filter if specified
        if include_prefixes:
            snapshot = GraphFilter.filter_by_prefixes(snapshot, include_prefixes)

        # Compute metrics
        metrics = MetricsCalculator.compute_metrics(snapshot)

        # Build output payload
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
        }

    @staticmethod
    def _build_graph_payload(
            snapshot: GraphSnapshot,
            metrics: Dict[str, object],
    ) -> Dict[str, object]:
        """Construct the complete graph.json payload.
        
        Args:
            snapshot: The graph data
            metrics: Computed metrics
            
        Returns:
            Dictionary ready for JSON serialization
        """
        formatted_nodes = NodeFormatter.format_nodes_with_metrics(snapshot, metrics)

        # Add node order to metrics for DSM correspondence
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


# Convenience function for backward compatibility
def build_graph(
        dot_directory: str,
        output_graph_path: str,
        output_dsm_path: Optional[str] = None,
        include_prefixes: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Build a dependency graph from DOT files.
    
    Args:
        dot_directory: Path to directory containing .dot files
        output_graph_path: Where to write graph.json
        output_dsm_path: Optional path for DSM.json output
        include_prefixes: Optional list of package prefixes to include
        
    Returns:
        Dictionary with build statistics and output paths
    """
    return GraphBuilder.build_graph(
        dot_directory,
        output_graph_path,
        output_dsm_path,
        include_prefixes,
    )