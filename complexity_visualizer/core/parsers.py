"""Parser for Graphviz DOT files from jdeps."""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .models import Graph, Node, Edge

EDGE_RE = re.compile(r'"([^"]+)"\s*->\s*"([^"]+)"')
TRAILING_PAREN_RE = re.compile(r"\s+\([^)]*\)$")
NOT_FOUND_RE = re.compile(r"\s*\(not found\)$", re.I)


def parse_dot_directory(
    dot_dir: str, include_prefixes: Optional[List[str]] = None
) -> Graph:
    """Parse all .dot files into a Graph.

    Args:
        dot_dir: Directory containing .dot files
        include_prefixes: If provided, only include nodes starting with these prefixes

    Returns:
        Graph with filtered nodes and edges
    """
    path = Path(dot_dir)
    if not path.is_dir():
        raise FileNotFoundError(f"Directory not found: {dot_dir}")

    nodes: Set[str] = set()
    unresolved: Set[str] = set()
    edges: Dict[Tuple[str, str], int] = defaultdict(int)
    excluded_nodes: Set[str] = set()

    for dot_file in path.glob("*.dot"):
        _parse_file(
            dot_file, nodes, unresolved, edges, excluded_nodes, include_prefixes
        )

    if include_prefixes and excluded_nodes:
        print(
            f"   Filtered: {len(nodes)} nodes included, {len(excluded_nodes)} external nodes excluded"
        )

    return Graph(
        nodes=[Node(id=nid) for nid in sorted(nodes)],
        edges=[Edge(from_id=s, to_id=t, weight=w) for (s, t), w in edges.items()],
        meta={"source": dot_dir, "unresolvedIds": sorted(unresolved)},
    )


def _should_include_node(node_id: str, prefixes: Optional[List[str]]) -> bool:
    """Check if node should be included based on prefix filters.

    Args:
        node_id: Node identifier (package/class name)
        prefixes: List of prefixes to include, None means include all

    Returns:
        True if node should be included, False otherwise
    """
    if not prefixes:
        return True
    return any(node_id.startswith(prefix) for prefix in prefixes)


def _parse_file(
    path: Path,
    nodes: Set[str],
    unresolved: Set[str],
    edges: Dict[Tuple[str, str], int],
    excluded_nodes: Set[str],
    include_prefixes: Optional[List[str]] = None,
) -> None:
    """Parse a single .dot file and populate nodes/edges sets.

    Args:
        path: Path to .dot file
        nodes: Set to populate with included nodes
        unresolved: Set to populate with unresolved dependencies
        edges: Dict to populate with edges
        excluded_nodes: Set to track excluded nodes
        include_prefixes: Optional list of prefixes to filter nodes
    """
    for line in path.read_text(encoding="utf-8").splitlines():
        if match := EDGE_RE.search(line):
            src_raw, tgt_raw = match.groups()
            src = _clean(src_raw)
            tgt = _clean(tgt_raw)

            src_included = _should_include_node(src, include_prefixes)
            tgt_included = _should_include_node(tgt, include_prefixes)

            if not src_included:
                excluded_nodes.add(src)
            if not tgt_included:
                excluded_nodes.add(tgt)

            if not (src_included and tgt_included):
                continue

            nodes.add(src)
            nodes.add(tgt)

            if NOT_FOUND_RE.search(src_raw):
                unresolved.add(src)
            if NOT_FOUND_RE.search(tgt_raw):
                unresolved.add(tgt)

            edges[(src, tgt)] += 1


def _clean(raw: str) -> str:
    """Remove trailing '(jar)' or similar."""
    return TRAILING_PAREN_RE.sub("", raw).strip()
