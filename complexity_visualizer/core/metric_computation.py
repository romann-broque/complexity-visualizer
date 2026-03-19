"""Orchestrate metric computation using the metric registry.

This module is now a thin wrapper around the metric calculator system,
providing backward compatibility while delegating actual computation
to the pluggable metric calculators.
"""

from typing import Dict, List, Optional

from .metrics import MetricContext, get_registry
from .metrics.algorithms import tarjan_scc
from .models import Graph

import complexity_visualizer.core.metrics.calculators


def compute_metrics(
    graph: Graph, source_metrics: Optional[Dict[str, Dict]] = None
) -> Dict:
    """Calculate all registered metrics for the graph.

    Args:
        graph: Dependency graph with nodes and edges
        source_metrics: Optional source code metrics (complexity, loc, is_abstract)

    Returns:
        Dict mapping metric name to list of values

    Raises:
        ValueError: If graph is empty or metric computation fails
    """
    if not graph.nodes:
        raise ValueError("Empty graph")

    n = len(graph.nodes)
    idx = graph.node_index()

    adj = [[] for _ in range(n)]
    for e in graph.edges:
        if (s := idx.get(e.from_id)) is not None and (
            t := idx.get(e.to_id)
        ) is not None:
            adj[s].append(t)

    context = MetricContext(
        graph=graph,
        adjacency_list=adj,
        node_index=idx,
        n_nodes=n,
        cache={},
        source_metrics=source_metrics,
    )

    registry = get_registry()
    metrics = registry.compute_all(context)

    if source_metrics:
        complexity_list = []
        loc_list = []

        for node in graph.nodes:
            src_metrics = source_metrics.get(node.id, {})
            complexity_list.append(src_metrics.get("complexity", 1))
            loc_list.append(src_metrics.get("loc", 0))

        metrics["complexity"] = complexity_list
        metrics["loc"] = loc_list
    else:
        metrics["complexity"] = [1] * n
        metrics["loc"] = [0] * n

    summary_metrics = {
        "nodeCount": n,
        "edgeCount": len(graph.edges),
        "scc": tarjan_scc(adj),
    }
    metrics.update(summary_metrics)

    return metrics
