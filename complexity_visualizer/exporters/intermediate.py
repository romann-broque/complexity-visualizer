"""Export graph data to intermediate JSON format.

This format is our flexible pivot format that can be converted
to CodeCharta, HTML, CSV, or other formats.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from complexity_visualizer.core.models import (
    Graph,
    Edge,
    NodeWithMetrics,
    NodeMetrics,
    Cycle,
    Summary,
    Hotspots,
    Aggregates,
    PackageStats,
    IntermediateFormat,
)


def export_intermediate(graph: Graph, metrics: Dict, output_path: str) -> None:
    """
    Export graph and metrics to intermediate JSON format.

    Args:
        graph: Graph object with nodes and edges
        metrics: Computed metrics dictionary from compute_metrics()
        output_path: Path to write metrics.json
    """
    # Build nodes with metrics
    nodes_with_metrics = _build_nodes_with_metrics(graph, metrics)

    # Build aggregates
    aggregates = _build_aggregates(graph, metrics, nodes_with_metrics)

    # Build package statistics
    packages = _build_package_stats(nodes_with_metrics)

    # Build metadata
    meta = {
        **graph.meta,
        "version": "2.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "format": "intermediate",
    }

    # Create intermediate format structure
    intermediate = IntermediateFormat(
        meta=meta,
        nodes=nodes_with_metrics,
        edges=graph.edges,
        aggregates=aggregates,
        packages=packages,
    )

    # Convert to dict and write JSON
    data = asdict(intermediate)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _build_nodes_with_metrics(graph: Graph, metrics: Dict) -> List[NodeWithMetrics]:
    """Build list of nodes with their metrics."""
    nodes_with_metrics = []

    for i, node in enumerate(graph.nodes):
        # Extract package from fully qualified name
        parts = node.id.rsplit(".", 1)
        package = parts[0] if len(parts) > 1 else ""
        name = parts[1] if len(parts) > 1 else node.id

        # Remove inner class markers
        name = name.replace("$", ".")

        node_metrics = NodeMetrics(
            fanIn=metrics["fanIn"][i],
            fanOut=metrics["fanOut"][i],
            transitiveDeps=metrics["transitiveDeps"][i],
            complexity=metrics["complexity"][i],
            loc=metrics["loc"][i],
            methods=metrics["methods"][i],
            maintenanceBurden=metrics["maintenanceBurden"][i],
            cycleParticipation=metrics.get(
                "cycleParticipation", [0] * len(graph.nodes)
            )[i],
            bidirectionalLinks=metrics.get(
                "bidirectionalLinks", [0] * len(graph.nodes)
            )[i],
            crossPackageDeps=metrics.get("crossPackageDeps", [0] * len(graph.nodes))[i],
            instability=metrics.get("instability", [0.0] * len(graph.nodes))[i],
        )

        nodes_with_metrics.append(
            NodeWithMetrics(
                id=node.id,
                name=name,
                type=node.type,
                package=package,
                metrics=node_metrics,
            )
        )

    return nodes_with_metrics


def _build_aggregates(
    graph: Graph, metrics: Dict, nodes: List[NodeWithMetrics]
) -> Aggregates:
    """Build aggregated statistics."""
    # Summary
    summary = Summary(
        totalClasses=metrics["nodeCount"],
        totalEdges=metrics["edgeCount"],
        avgComplexity=sum(metrics["complexity"]) / max(1, len(metrics["complexity"])),
        avgFanOut=sum(metrics["fanOut"]) / max(1, len(metrics["fanOut"])),
        cycleCount=sum(1 for scc in metrics["scc"] if len(scc) > 1),
    )

    # Cycles
    cycles = []
    for i, scc in enumerate(metrics["scc"]):
        if len(scc) > 1:  # Only actual cycles
            node_ids = [graph.nodes[idx].id for idx in scc]
            cycles.append(Cycle(id=i, nodes=node_ids, size=len(scc)))

    # Hotspots
    hotspots = _identify_hotspots(nodes)

    return Aggregates(summary=summary, cycles=cycles, hotspots=hotspots)


def _identify_hotspots(nodes: List[NodeWithMetrics], top_n: int = 10) -> Hotspots:
    """Identify problematic classes (hotspots)."""
    # Sort by different criteria
    by_complexity = sorted(nodes, key=lambda n: n.metrics.complexity, reverse=True)
    by_fan_out = sorted(nodes, key=lambda n: n.metrics.fanOut, reverse=True)
    by_burden = sorted(nodes, key=lambda n: n.metrics.maintenanceBurden, reverse=True)

    return Hotspots(
        highComplexity=[
            n.id for n in by_complexity[:top_n] if n.metrics.complexity > 5
        ],
        highFanOut=[n.id for n in by_fan_out[:top_n] if n.metrics.fanOut > 5],
        highBurden=[
            n.id for n in by_burden[:top_n] if n.metrics.maintenanceBurden > 50
        ],
    )


def _build_package_stats(nodes: List[NodeWithMetrics]) -> Dict[str, PackageStats]:
    """Build statistics per package."""
    packages: Dict[str, List[NodeWithMetrics]] = {}

    # Group nodes by package
    for node in nodes:
        if node.package:
            if node.package not in packages:
                packages[node.package] = []
            packages[node.package].append(node)

    # Compute stats per package
    stats = {}
    for package, pkg_nodes in packages.items():
        stats[package] = PackageStats(
            classCount=len(pkg_nodes),
            avgComplexity=sum(n.metrics.complexity for n in pkg_nodes) / len(pkg_nodes),
            totalLoc=sum(n.metrics.loc for n in pkg_nodes),
        )

    return stats
