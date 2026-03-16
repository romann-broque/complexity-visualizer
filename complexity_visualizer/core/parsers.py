"""Parser for Graphviz DOT files from jdeps."""
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, Tuple

from .models import Graph, Node, Edge

EDGE_RE = re.compile(r'"([^"]+)"\s*->\s*"([^"]+)"')
TRAILING_PAREN_RE = re.compile(r"\s+\([^)]*\)$")
NOT_FOUND_RE = re.compile(r"\s*\(not found\)$", re.I)


def parse_dot_directory(dot_dir: str) -> Graph:
    """Parse all .dot files into a Graph."""
    path = Path(dot_dir)
    if not path.is_dir():
        raise FileNotFoundError(f"Directory not found: {dot_dir}")

    nodes: Set[str] = set()
    unresolved: Set[str] = set()
    edges: Dict[Tuple[str, str], int] = defaultdict(int)

    for dot_file in path.glob("*.dot"):
        _parse_file(dot_file, nodes, unresolved, edges)

    return Graph(
        nodes=[Node(id=nid) for nid in sorted(nodes)],
        edges=[Edge(from_id=s, to_id=t, weight=w) for (s, t), w in edges.items()],
        meta={"source": dot_dir, "unresolvedIds": sorted(unresolved)}
    )


def _parse_file(
        path: Path,
        nodes: Set[str],
        unresolved: Set[str],
        edges: Dict[Tuple[str, str], int]
) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if match := EDGE_RE.search(line):
            src_raw, tgt_raw = match.groups()
            src = _clean(src_raw)
            tgt = _clean(tgt_raw)

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