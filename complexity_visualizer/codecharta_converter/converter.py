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
        input_path: str,
        output_path: str,
        project_name: Optional[str] = None
) -> None:
    """Convert graph.json to CodeCharta format."""
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))

    if not project_name:
        project_name = data.get("meta", {}).get("project", "project")

    root = CCNode(name=project_name, type="Folder")
    paths = {}

    # Build tree
    for node in data["nodes"]:
        fqn = node["id"]
        metrics = node.get("metrics", {})

        attrs = {
            "fanIn": metrics.get("fanIn", 0),
            "fanOut": metrics.get("fanOut", 0),
            "changeCost": metrics.get("changeCost", 0)
        }

        path = _add_node(root, fqn, attrs)
        paths[fqn] = path

    # Convert edges
    edges = []
    for edge in data.get("edges", []):
        src = paths.get(edge["from_id"])
        tgt = paths.get(edge["to_id"])
        if src and tgt:
            edges.append({
                "fromNodeName": src,
                "toNodeName": tgt,
                "attributes": {"weight": edge.get("weight", 1)}
            })

    # Output
    output = {
        "projectName": project_name,
        "apiVersion": "1.0",
        "nodes": [root.to_dict()],
        "edges": edges,
        "attributeTypes": {
            "fanIn": "absolute",
            "fanOut": "absolute",
            "changeCost": "absolute"
        }
    }

    Path(output_path).write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")


def _add_node(root: CCNode, fqn: str, attrs: Dict) -> str:
    """Add class node to tree, return absolute path."""
    segments = fqn.replace("/", ".").split(".")
    segments[-1] = segments[-1].replace("$", ".")

    # Navigate to parent folder
    current = root
    for seg in segments[:-1]:
        child = next((c for c in current.children if c.name == seg and c.type == "Folder"), None)
        if not child:
            child = CCNode(name=seg, type="Folder")
            current.children.append(child)
        current = child

    # Add file node
    class_name = segments[-1]
    file_node = CCNode(name=class_name, type="File", attributes=attrs)
    current.children.append(file_node)

    return "/" + "/".join(segments)