from __future__ import annotations
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .models import GraphSnapshot
from .dot_parser import parse_dot_directory
from .metrics import compute_metrics, build_dsm
from .util_io import ensure_parent_dir, write_json

from typing import Iterable, Set

def _filter_snapshot_by_prefixes(
        snapshot: GraphSnapshot,
        include_prefixes: Iterable[str],
) -> GraphSnapshot:
    """
    Conserve uniquement les nœuds dont l'id commence par l'un des préfixes fournis
    et les arêtes entièrement internes à ce sous-graphe.
    """
    prefixes: Tuple[str, ...] = tuple(include_prefixes)
    if not prefixes:
        return snapshot

    # 1) Nodes to keep
    kept_ids: Set[str] = {
        n.id for n in snapshot.nodes
        if any(n.id.startswith(p) for p in prefixes)
    }

    # 2) Filtered nodes, preserved order
    nodes_kept = [n for n in snapshot.nodes if n.id in kept_ids]

    # 3) Edges with two kept ends
    edges_kept = [
        e for e in snapshot.edges
        if e.from_id in kept_ids and e.to_id in kept_ids
    ]

    # 4) Filtered Meta (ex: unresolvedIds)
    meta = dict(snapshot.meta)
    if "unresolvedIds" in meta:
        meta["unresolvedIds"] = [i for i in meta["unresolvedIds"] if i in kept_ids]

    return GraphSnapshot(nodes=nodes_kept, edges=edges_kept, meta=meta)

def _extract_class_name(node_id: str) -> str:
    """
    Simple class name from FQCN:
    - take last segment after '.' or '/' if any
    - map inner classes A$B -> A.B
    """
    right = node_id.rsplit("/", 1)[-1]
    simple = right.rsplit(".", 1)[-1] if "." in right else right
    return simple.replace("$", ".")

def _denormalize_node_metrics(
        snapshot: GraphSnapshot,
        metrics: Dict[str, object]
) -> List[Dict[str, object]]:
    fan_out: List[int] = metrics["fanOut"]  # type: ignore[index]
    fan_in: List[int] = metrics["fanIn"]    # type: ignore[index]
    instability: List[float] = metrics["instability"]  # type: ignore[index]

    unresolved_set = set(snapshot.meta.get("unresolvedIds", []))

    out: List[Dict[str, object]] = []
    for i, node in enumerate(snapshot.nodes):
        nid = node.id
        out.append({
            "id": nid,
            "type": node.type,
            "name": _extract_class_name(nid),
            "unresolved": (nid in unresolved_set),
            "metrics": {
                "fanOut": fan_out[i],
                "fanIn":  fan_in[i],
                "stability": 1 - instability[i],
            },
        })
    return out

def build_graph(
        dot_dir: str,
        out_graph: str,
        out_dsm: Optional[str] = None,
        include_prefixes: Optional[List[str]] = None,
) -> dict:
    """Parse DOT -> (filtre optionnel) -> calcule métriques -> écrit JSON(s)."""
    ensure_parent_dir(out_graph)
    if out_dsm:
        ensure_parent_dir(out_dsm)

    snapshot: GraphSnapshot = parse_dot_directory(dot_dir)
    snapshot.meta.setdefault("generatedAt", datetime.now(timezone.utc).isoformat())

    # >>> FILTER PER PREFIXES (optional)
    if include_prefixes:
        snapshot = _filter_snapshot_by_prefixes(snapshot, include_prefixes)

    metrics = compute_metrics(snapshot)
    metrics_with_order = {**metrics, "order": [n.id for n in snapshot.nodes]}

    nodes_out = _denormalize_node_metrics(snapshot, metrics)

    payload = {
        "meta": snapshot.meta,
        "nodes": nodes_out,
        "edges": [asdict(e) for e in snapshot.edges],
        "metrics": metrics_with_order,
    }
    write_json(out_graph, payload)

    dsm_written = None
    if out_dsm:
        dsm = build_dsm(snapshot)
        write_json(out_dsm, dsm)
        dsm_written = out_dsm

    return {
        "nodeCount": metrics["nodeCount"],
        "edgeCount": metrics["edgeCount"],
        "graphPath": out_graph,
        "dsmPath": dsm_written,
    }
