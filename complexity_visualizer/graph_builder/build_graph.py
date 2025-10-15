"""Build graph.json from DOT files."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .dot_parser import parse_dot_directory
from .metrics import compute_metrics
from .models import Graph


def build_graph(
        dot_dir: str,
        output_path: str,
        prefixes: Optional[List[str]] = None
) -> Dict:
    """Parse DOT files, compute metrics, write graph.json."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    graph = parse_dot_directory(dot_dir)

    if prefixes:
        graph = _filter_by_prefix(graph, prefixes)

    metrics = compute_metrics(graph)
    graph.meta["generatedAt"] = datetime.now(timezone.utc).isoformat()

    # Build output
    payload = {
        "meta": graph.meta,
        "nodes": _format_nodes(graph, metrics),
        "edges": [{"from_id": e.from_id, "to_id": e.to_id, "weight": e.weight} for e in graph.edges],
        "metrics": metrics
    }

    Path(output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "nodeCount": metrics["nodeCount"],
        "edgeCount": metrics["edgeCount"],
        "graphPath": output_path
    }


def _filter_by_prefix(graph: Graph, prefixes: List[str]) -> Graph:
    kept = {n.id for n in graph.nodes if any(n.id.startswith(p) for p in prefixes)}
    return Graph(
        nodes=[n for n in graph.nodes if n.id in kept],
        edges=[e for e in graph.edges if e.from_id in kept and e.to_id in kept],
        meta={**graph.meta, "unresolvedIds": [u for u in graph.meta.get("unresolvedIds", []) if u in kept]}
    )


def _format_nodes(graph: Graph, metrics: Dict) -> List[Dict]:
    nodes = []
    for i, node in enumerate(graph.nodes):
        nodes.append({
            "id": node.id,
            "type": node.type,
            "name": node.id.rsplit(".", 1)[-1].rsplit("/", 1)[-1].replace("$", "."),
            "metrics": {
                "fanIn": metrics["fanIn"][i],
                "fanOut": metrics["fanOut"][i],
                "changeCost": metrics["changeCost"][i]
            }
        })
    return nodes