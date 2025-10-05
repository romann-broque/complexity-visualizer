# src/complexity_visualizer/dot_parser.py
from __future__ import annotations
import os, re
from typing import Dict, List, Set, Tuple
from .models import GraphSnapshot, Node, Edge

_TRAILING_PAREN_RE = re.compile(r"\s+\([^)]*\)$")          # strip " (…jar)" / " (not found)"
_NOT_FOUND_RE      = re.compile(r"\s*\(not found\)$", re.IGNORECASE)
_EDGE_RE           = re.compile(r'"([^"]+)"\s*->\s*"([^"]+)"\s*;')

def _canonical_id(raw: str) -> str:
    return _TRAILING_PAREN_RE.sub("", raw).strip()

def _is_not_found_label(raw: str) -> bool:
    return bool(_NOT_FOUND_RE.search(raw))

def _last_segment(fqname: str) -> str:
    right = fqname.rsplit("/", 1)[-1]
    return right.rsplit(".", 1)[-1] if "." in right else right

def _is_probable_java_class(fqname: str) -> bool:
    """
    Heuristique robuste:
      - on regarde le dernier segment (après '.' ou '/')
      - une classe Java a presque toujours au moins UNE majuscule (Foo, UserDTO, A$Inner)
      - les inner classes utilisent '$' → on l’accepte aussi
    """
    seg = _last_segment(fqname)
    return ("$" in seg) or any(c.isupper() for c in seg)

def parse_dot_directory(dot_dir: str) -> GraphSnapshot:
    if not os.path.isdir(dot_dir):
        raise FileNotFoundError(f"DOT directory not found: {dot_dir}")

    # On agrège les arêtes sur (from,to) et l’on garde uniquement les classes
    class_ids: Set[str] = set()
    unresolved_class_ids: Set[str] = set()
    edge_weights: Dict[Tuple[str, str], int] = {}

    for name in os.listdir(dot_dir):
        if not name.endswith(".dot"):
            continue
        with open(os.path.join(dot_dir, name), encoding="utf-8") as f:
            for line in f:
                m = _EDGE_RE.search(line)
                if not m:
                    continue
                raw_a, raw_b = m.group(1), m.group(2)

                can_a, can_b = _canonical_id(raw_a), _canonical_id(raw_b)
                a_is_class   = _is_probable_java_class(can_a)
                b_is_class   = _is_probable_java_class(can_b)

                # On ne conserve que les relations entre classes (=> filtre les packages)
                if not (a_is_class and b_is_class):
                    continue

                class_ids.add(can_a); class_ids.add(can_b)

                if _is_not_found_label(raw_a):
                    unresolved_class_ids.add(can_a)
                if _is_not_found_label(raw_b):
                    unresolved_class_ids.add(can_b)

                edge_weights[(can_a, can_b)] = edge_weights.get((can_a, can_b), 0) + 1

    node_objs = [Node(id=n, type="class") for n in sorted(class_ids)]
    edges = [Edge(from_id=a, to_id=b, weight=w) for (a, b), w in edge_weights.items()]

    meta = {
        "language": "java",
        "source": dot_dir,
        "unresolvedIds": sorted(unresolved_class_ids),
        "filtered": "packages-removed"  # trace utile pour déboguer
    }
    return GraphSnapshot(nodes=node_objs, edges=edges, meta=meta)
