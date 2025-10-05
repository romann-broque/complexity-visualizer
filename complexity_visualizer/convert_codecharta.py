from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class CCNode:
    name: str
    type: str = "Folder"  # "Folder" or "File"
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List["CCNode"] = field(default_factory=list)

    def to_json(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "attributes": self.attributes,
        }
        if self.children:
            payload["children"] = [c.to_json() for c in self.children]
        return payload


def _class_path_parts(fqcn: str) -> List[str]:
    """
    Transforme un FQCN Java en segments de chemin. Ex:
      com.org.pkg.ClassA  -> ["com","org","pkg","ClassA"]
    Gestion simple: remplace '$' (inner classes) par '.' uniquement pour l’affichage (le segment final).
    """
    parts = fqcn.strip().split(".")
    if not parts:
        return [fqcn]
    parts[-1] = parts[-1].replace("$", ".")
    return parts


def _ensure_folder(root: CCNode, path_parts: List[str]) -> CCNode:
    """Crée/récupère récursivement un nœud dossier pour path_parts (sans la feuille)."""
    node = root
    for part in path_parts:
        # Find or create subdirectory
        child = next((c for c in node.children if c.name == part and c.type == "Folder"), None)
        if child is None:
            child = CCNode(name=part, type="Folder")
            node.children.append(child)
        node = child
    return node


def _add_leaf(root: CCNode, fqcn: str, attrs: Dict[str, Any]) -> str:
    """
    Ajoute une feuille (File) pour la classe avec ses attributes.
    Retourne le chemin absolu CodeCharta (ex: /com/org/pkg/ClassA).
    """
    parts = _class_path_parts(fqcn)
    if len(parts) == 1:
        folder_parts: List[str] = []
        leaf_name = parts[0]
    else:
        folder_parts = parts[:-1]
        leaf_name = parts[-1]

    folder_node = _ensure_folder(root, folder_parts)
    file_node = next((c for c in folder_node.children if c.name == leaf_name and c.type == "File"), None)
    if file_node is None:
        file_node = CCNode(name=leaf_name, type="File", attributes=attrs)
        folder_node.children.append(file_node)
    else:
        # Merge/Overwrite attributes if already present
        file_node.attributes.update(attrs)

    return "/" + "/".join(parts)


def convert_graph_to_codecharta(
        graph_json: Dict[str, Any],
        project_name: str = "complexity-visualizer",
) -> Dict[str, Any]:
    """
    Convertit le graph.json maison en un codecharta.json compatible.
    - Les classes deviennent des "File" avec attributes { fanIn, fanOut, instability, unresolved }
    - Les packages deviennent des "Folder"
    - Les edges sont conservées (poids = weight)
    """
    nodes_in: List[Dict[str, Any]] = graph_json.get("nodes", [])
    edges_in: List[Dict[str, Any]] = graph_json.get("edges", [])

    root = CCNode(name=project_name, type="Folder")

    # Map: id FQCN -> chemin CodeCharta (/a/b/C)
    id_to_path: Dict[str, str] = {}

    # 1) Add all leaves with their attributes
    for n in nodes_in:
        fqcn: str = n["id"]
        m = n.get("metrics", {}) or {}
        attrs = {
            "fanIn": int(m.get("fanIn", 0)),
            "fanOut": int(m.get("fanOut", 0)),
            "stability": float(1 - m.get("instability", 0.0)),
            "unresolved": 1 if n.get("unresolved") else 0,
        }
        path = _add_leaf(root, fqcn, attrs)
        id_to_path[fqcn] = path

    # 2) Transform edges (if missing, ignored)
    cc_edges: List[Dict[str, Any]] = []
    for e in edges_in:
        src_id: str = e.get("from_id") or e.get("from") or ""
        dst_id: str = e.get("to_id") or e.get("to") or ""
        if not src_id or not dst_id:
            continue
        src_path = id_to_path.get(src_id)
        dst_path = id_to_path.get(dst_id)
        if not src_path or not dst_path:
            # external edge (past filtered)
            continue
        cc_edges.append({
            "fromNodeName": src_path,
            "toNodeName": dst_path,
            "attributes": {
                "weight": int(e.get("weight", 1))
            }
        })

    # 3) Attribute types (help visualizer for colors/scales)
    attribute_types = {
        "fanIn": "absolute",
        "fanOut": "absolute",
        "stability": "relative",
        "unresolved": "absolute",
        "weight": "absolute"
    }

    # 4) Final payload
    cc_json = {
        "projectName": project_name,
        "apiVersion": "1.0",
        "nodes": [root.to_json()],
        "edges": cc_edges,
        "attributeTypes": attribute_types
    }
    return cc_json


def convert_file(in_path: str, out_path: str, project_name: Optional[str] = None) -> None:
    with open(in_path, "r", encoding="utf-8") as f:
        g = json.load(f)
    cc = convert_graph_to_codecharta(g, project_name or g.get("meta", {}).get("project", "complexity-visualizer"))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cc, f, indent=2, ensure_ascii=False)
