"""Convert graph.json to CodeCharta format."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CCNode:
    name: str
    type: str = "Folder"
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List["CCNode"] = field(default_factory=list)

    def to_dict(self) -> Dict:
        d = {"name": self.name, "type": self.type, "attributes": self.attributes}
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d


def convert_to_codecharta(
    input_path: str, output_path: str, project_name: Optional[str] = None
) -> None:
    """Convert graph.json to CodeCharta format."""
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))

    if not project_name:
        project_name = (
            data.get("meta", {}).get("projectName")
            or data.get("meta", {}).get("project")
            or "project"
        )

    # Ensure project_name is not None (type narrowing)
    assert project_name is not None

    # Filter nodes - only keep actual classes (not packages)
    all_nodes = data["nodes"]
    class_nodes = [n for n in all_nodes if n.get("type") != "package"]
    package_nodes = [n for n in all_nodes if n.get("type") == "package"]

    print(f"   Converting: {len(class_nodes)} classes")
    if package_nodes:
        print(f"   Excluding: {len(package_nodes)} packages")

    root = CCNode(name=project_name, type="Folder")
    paths = {}

    # Build tree (only from classes)
    for node in class_nodes:
        fqn = node["id"]
        metrics = node.get("metrics", {})

        attrs = {
            "fanIn": metrics.get("fanIn", 0),
            "fanOut": metrics.get("fanOut", 0),
            "transitiveDeps": metrics.get("transitiveDeps", 0),
            "complexity": metrics.get("complexity", 1),
            "loc": metrics.get("loc", 0),
            "methods": metrics.get("methods", 0),
            "maintenanceBurden": metrics.get("maintenanceBurden", 0),
            "cycleParticipation": metrics.get("cycleParticipation", 0),
            "bidirectionalLinks": metrics.get("bidirectionalLinks", 0),
            "crossPackageDeps": metrics.get("crossPackageDeps", 0),
            "instability": metrics.get("instability", 0.0),
        }

        path = _add_node(root, fqn, attrs)
        paths[fqn] = path

    # Filter edges - remove references to packages
    package_ids = {n["id"] for n in package_nodes}
    all_edges = data.get("edges", [])
    valid_edges = [
        e
        for e in all_edges
        if e["from_id"] not in package_ids and e["to_id"] not in package_ids
    ]

    if len(valid_edges) < len(all_edges):
        excluded_edges = len(all_edges) - len(valid_edges)
        print(
            f"   Edges: {len(valid_edges)} kept, {excluded_edges} excluded (package dependencies)"
        )

    # Convert edges
    edges = []
    for edge in valid_edges:
        src = paths.get(edge["from_id"])
        tgt = paths.get(edge["to_id"])
        if src and tgt:
            edges.append(
                {
                    "fromNodeName": src,
                    "toNodeName": tgt,
                    "attributes": {"weight": edge.get("weight", 1)},
                }
            )

    # Output
    output = {
        "projectName": project_name,
        "apiVersion": "1.0",
        "nodes": [root.to_dict()],
        "edges": edges,
        "attributeTypes": {
            "fanIn": "absolute",
            "fanOut": "absolute",
            "transitiveDeps": "absolute",
            "complexity": "absolute",
            "loc": "absolute",
            "methods": "absolute",
            "maintenanceBurden": "absolute",
            "cycleParticipation": "absolute",
            "bidirectionalLinks": "absolute",
            "crossPackageDeps": "absolute",
            "instability": "relative",
        },
    }

    Path(output_path).write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _add_node(root: CCNode, fqn: str, attrs: Dict) -> str:
    """Add class node to tree, return absolute path."""
    segments = fqn.replace("/", ".").split(".")
    segments[-1] = segments[-1].replace("$", ".")

    # Navigate to parent folder
    current = root
    for seg in segments[:-1]:
        child = next(
            (c for c in current.children if c.name == seg and c.type == "Folder"), None
        )
        if not child:
            child = CCNode(name=seg, type="Folder")
            current.children.append(child)
        current = child

    # Add file node
    class_name = segments[-1]
    file_node = CCNode(name=class_name, type="File", attributes=attrs)
    current.children.append(file_node)

    return "/" + "/".join(segments)
