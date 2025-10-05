"""Converter from internal graph format to CodeCharta format.

This module transforms the internal dependency graph representation
into the format expected by CodeCharta visualization tool.

CodeCharta uses a hierarchical file-tree structure where:
- Packages become Folders
- Classes become Files with metrics as attributes
- Dependencies become edges with weights
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CodeChartaNode:
    """Represents a node in the CodeCharta tree structure."""

    name: str
    type: str = "Folder"  # "Folder" or "File"
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List["CodeChartaNode"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for JSON serialization."""
        result: Dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "attributes": self.attributes,
        }
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        return result


class CodeChartaConverter:
    """Converts internal graph format to CodeCharta format."""

    @staticmethod
    def convert_graph(
            graph_data: Dict[str, Any],
            project_name: str = "complexity-visualizer",
    ) -> Dict[str, Any]:
        """Convert graph.json to CodeCharta format.
        
        Args:
            graph_data: Internal graph representation
            project_name: Name for the root node
            
        Returns:
            Dictionary in CodeCharta format ready for JSON serialization
        """
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        root = CodeChartaNode(name=project_name, type="Folder")
        node_id_to_path: Dict[str, str] = {}

        # Build tree structure and collect node paths
        for node in nodes:
            fully_qualified_name: str = node["id"]
            metrics = node.get("metrics", {}) or {}

            attributes = {
                "fanIn": int(metrics.get("fanIn", 0)),
                "fanOut": int(metrics.get("fanOut", 0)),
                "stability": float(metrics.get("stability", 0.0)),
                "unresolved": 1 if node.get("unresolved") else 0,
            }

            path = CodeChartaConverter._add_class_node(
                root, fully_qualified_name, attributes
            )
            node_id_to_path[fully_qualified_name] = path

        # Convert edges
        codecharta_edges = CodeChartaConverter._convert_edges(
            edges, node_id_to_path
        )

        # Define attribute types for visualization
        attribute_types = {
            "fanIn": "absolute",
            "fanOut": "absolute",
            "stability": "relative",
            "unresolved": "absolute",
            "weight": "absolute",
        }

        return {
            "projectName": project_name,
            "apiVersion": "1.0",
            "nodes": [root.to_dict()],
            "edges": codecharta_edges,
            "attributeTypes": attribute_types,
        }

    @staticmethod
    def convert_file(
            input_path: str,
            output_path: str,
            project_name: Optional[str] = None,
    ) -> None:
        """Convert a graph.json file to codecharta.json format.
        
        Args:
            input_path: Path to graph.json
            output_path: Path where codecharta.json should be written
            project_name: Optional custom project name
        """
        with open(input_path, "r", encoding="utf-8") as file:
            graph_data = json.load(file)

        # Use project name from metadata if not specified
        if project_name is None:
            project_name = (
                    graph_data.get("meta", {}).get("project")
                    or "complexity-visualizer"
            )

        codecharta_data = CodeChartaConverter.convert_graph(
            graph_data, project_name
        )

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(codecharta_data, file, indent=2, ensure_ascii=False)

    @staticmethod
    def _parse_class_path(fully_qualified_name: str) -> List[str]:
        """Transform a fully qualified class name into path segments.
        
        Args:
            fully_qualified_name: e.g., "com.org.pkg.ClassA" or "com.org.Outer$Inner"
            
        Returns:
            List of path segments, e.g., ["com", "org", "pkg", "ClassA"]
            
        Note:
            Inner classes marked with '$' are converted to '.' for display
        """
        segments = fully_qualified_name.strip().split(".")
        if not segments:
            return [fully_qualified_name]

        # Convert inner class marker for better readability
        segments[-1] = segments[-1].replace("$", ".")
        return segments

    @staticmethod
    def _ensure_folder_path(
            root: CodeChartaNode,
            path_segments: List[str],
    ) -> CodeChartaNode:
        """Create or retrieve folder nodes for a path.
        
        Args:
            root: Root node to start from
            path_segments: List of folder names to traverse/create
            
        Returns:
            The deepest folder node in the path
        """
        current_node = root

        for segment in path_segments:
            # Look for existing folder child
            child = next(
                (c for c in current_node.children
                 if c.name == segment and c.type == "Folder"),
                None
            )

            if child is None:
                child = CodeChartaNode(name=segment, type="Folder")
                current_node.children.append(child)

            current_node = child

        return current_node

    @staticmethod
    def _add_class_node(
            root: CodeChartaNode,
            fully_qualified_name: str,
            attributes: Dict[str, Any],
    ) -> str:
        """Add a class as a File node in the tree.
        
        Args:
            root: Root of the tree
            fully_qualified_name: Full class name
            attributes: Metrics to attach to the node
            
        Returns:
            Absolute CodeCharta path (e.g., "/com/org/pkg/ClassA")
        """
        path_segments = CodeChartaConverter._parse_class_path(fully_qualified_name)

        if len(path_segments) == 1:
            # Class at root level
            folder_segments: List[str] = []
            class_name = path_segments[0]
        else:
            # Class in package
            folder_segments = path_segments[:-1]
            class_name = path_segments[-1]

        # Navigate to or create parent folder
        parent_folder = CodeChartaConverter._ensure_folder_path(
            root, folder_segments
        )

        # Create or update file node
        file_node = next(
            (c for c in parent_folder.children
             if c.name == class_name and c.type == "File"),
            None
        )

        if file_node is None:
            file_node = CodeChartaNode(
                name=class_name,
                type="File",
                attributes=attributes,
            )
            parent_folder.children.append(file_node)
        else:
            # Merge attributes if node already exists
            file_node.attributes.update(attributes)

        return "/" + "/".join(path_segments)

    @staticmethod
    def _convert_edges(
            edges: List[Dict[str, Any]],
            node_id_to_path: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Convert internal edge format to CodeCharta edge format.
        
        Args:
            edges: List of edges from internal format
            node_id_to_path: Mapping from node IDs to CodeCharta paths
            
        Returns:
            List of edges in CodeCharta format
        """
        codecharta_edges: List[Dict[str, Any]] = []

        for edge in edges:
            source_id: str = edge.get("from_id") or edge.get("from") or ""
            target_id: str = edge.get("to_id") or edge.get("to") or ""

            if not source_id or not target_id:
                continue

            source_path = node_id_to_path.get(source_id)
            target_path = node_id_to_path.get(target_id)

            if not source_path or not target_path:
                # External edge (filtered out)
                continue

            codecharta_edges.append({
                "fromNodeName": source_path,
                "toNodeName": target_path,
                "attributes": {
                    "weight": int(edge.get("weight", 1))
                }
            })

        return codecharta_edges


# Convenience function for backward compatibility
def convert_graph_to_codecharta(
        graph_data: Dict[str, Any],
        project_name: str = "complexity-visualizer",
) -> Dict[str, Any]:
    """Convert graph.json to CodeCharta format."""
    return CodeChartaConverter.convert_graph(graph_data, project_name)


def convert_file(
        input_path: str,
        output_path: str,
        project_name: Optional[str] = None,
) -> None:
    """Convert a graph.json file to codecharta.json."""
    CodeChartaConverter.convert_file(input_path, output_path, project_name)