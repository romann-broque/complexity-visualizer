"""Converter from graph.json to CodeCharta format.

Transforms internal dependency graph representation into CodeCharta
visualization format with hierarchical tree structure.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class CodeChartaNode:
    """Node in CodeCharta tree structure."""
    name: str
    type: str = "Folder"  # "Folder" or "File"
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List["CodeChartaNode"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        result: Dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "attributes": self.attributes,
        }
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        return result


class CodeChartaConverter:
    """Converts graph.json to CodeCharta format."""

    @staticmethod
    def convert_graph(
            graph_data: Dict[str, Any],
            project_name: str = "project",
    ) -> Dict[str, Any]:
        """Convert graph.json to CodeCharta format with enhanced metrics.

        Args:
            graph_data: Internal graph representation
            project_name: Name for root node

        Returns:
            Dict in CodeCharta format ready for JSON
        """
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        metrics = graph_data.get("metrics", {})

        root = CodeChartaNode(name=project_name, type="Folder")
        node_id_to_path: Dict[str, str] = {}

        # Extract enhanced metrics for nodes
        node_enhanced = CodeChartaConverter._extract_node_enhanced_metrics(
            nodes, metrics
        )

        # Build tree structure
        for idx, node in enumerate(nodes):
            fqn: str = node["id"]
            base_metrics = node.get("metrics", {}) or {}
            enhanced = node_enhanced.get(idx, {})

            attributes = {
                # Base coupling
                "fanIn": int(base_metrics.get("fanIn", 0)),
                "fanOut": int(base_metrics.get("fanOut", 0)),
                "stability": float(base_metrics.get("stability", 0.0)),
                "instability": round(1.0 - float(base_metrics.get("stability", 0.0)), 3),
                "totalCoupling": int(base_metrics.get("fanIn", 0)) + int(base_metrics.get("fanOut", 0)),

                # Enhanced
                "transitiveDeps": enhanced.get("transitiveDeps", 0),
                "isInCycle": 1 if enhanced.get("isInCycle", False) else 0,
                "cycleSize": enhanced.get("cycleSize", 0),
                "isBreakingPoint": 1 if enhanced.get("isBreakingPoint", False) else 0,
                "isHighImpact": 1 if enhanced.get("isHighImpact", False) else 0,
                "isHubNode": 1 if enhanced.get("isHubNode", False) else 0,

                # Architectural
                "isLeafNode": 1 if base_metrics.get("fanOut", 0) == 0 else 0,
                "isRootNode": 1 if base_metrics.get("fanIn", 0) == 0 else 0,

                # Status
                "unresolved": 1 if node.get("unresolved") else 0,
            }

            path = CodeChartaConverter._add_class_node(root, fqn, attributes)
            node_id_to_path[fqn] = path

        # Convert edges
        cc_edges = CodeChartaConverter._convert_edges(edges, node_id_to_path)

        # Attribute types
        attribute_types = {
            "fanIn": "absolute",
            "fanOut": "absolute",
            "stability": "relative",
            "instability": "relative",
            "totalCoupling": "absolute",
            "transitiveDeps": "absolute",
            "isInCycle": "absolute",
            "cycleSize": "absolute",
            "isBreakingPoint": "absolute",
            "isHighImpact": "absolute",
            "isHubNode": "absolute",
            "isLeafNode": "absolute",
            "isRootNode": "absolute",
            "unresolved": "absolute",
            "weight": "absolute",
        }

        # Metadata
        metadata = {
            "exportedMetrics": attribute_types,
            "visualizationRecommendations": {
                "problemDetection": {
                    "area": "fanIn",
                    "height": "fanOut",
                    "color": "instability"
                },
                "refactoringImpact": {
                    "area": "transitiveDeps",
                    "height": "totalCoupling",
                    "color": "isInCycle"
                },
                "architecturalHealth": {
                    "area": "totalCoupling",
                    "height": "transitiveDeps",
                    "color": "isHubNode"
                }
            }
        }

        return {
            "projectName": project_name,
            "apiVersion": "1.0",
            "nodes": [root.to_dict()],
            "edges": cc_edges,
            "attributeTypes": attribute_types,
            "metadata": metadata,
        }

    @staticmethod
    def _extract_node_enhanced_metrics(
            nodes: List[Dict[str, Any]],
            metrics: Dict[str, Any],
    ) -> Dict[int, Dict[str, Any]]:
        """Extract enhanced metrics per node from global metrics."""
        node_enhanced: Dict[int, Dict[str, Any]] = {}

        # Extract cycle info
        scc = metrics.get("scc", [])
        cycles = [c for c in scc if len(c) > 1]

        nodes_in_cycles: Set[int] = set()
        cycle_size_map: Dict[int, int] = {}
        for cycle in cycles:
            for node_idx in cycle:
                nodes_in_cycles.add(node_idx)
                cycle_size_map[node_idx] = len(cycle)

        # Extract refactoring metrics
        refactoring = metrics.get("refactoring", {})
        high_impact_threshold = max(10, len(nodes) // 10)

        for idx, node in enumerate(nodes):
            base = node.get("metrics", {}) or {}
            fan_in = base.get("fanIn", 0)
            fan_out = base.get("fanOut", 0)
            total_coupling = fan_in + fan_out

            # Estimate transitive (would be computed in enhanced_metrics)
            transitive_estimate = fan_out * 2

            node_enhanced[idx] = {
                "isInCycle": idx in nodes_in_cycles,
                "cycleSize": cycle_size_map.get(idx, 0),
                "transitiveDeps": transitive_estimate,
                "isBreakingPoint": False,  # Simplified
                "isHighImpact": transitive_estimate >= high_impact_threshold,
                "isHubNode": total_coupling >= 10,
            }

        return node_enhanced

    @staticmethod
    def convert_file(
            input_path: str,
            output_path: str,
            project_name: Optional[str] = None,
    ) -> None:
        """Convert graph.json file to codecharta.json.

        Args:
            input_path: Path to graph.json
            output_path: Where to write codecharta.json
            project_name: Optional custom project name
        """
        with open(input_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        if project_name is None:
            project_name = (
                    graph_data.get("meta", {}).get("project") or "project"
            )

        cc_data = CodeChartaConverter.convert_graph(graph_data, project_name)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cc_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _parse_class_path(fqn: str) -> List[str]:
        """Transform FQN to path segments.

        'com.org.pkg.ClassA' -> ['com', 'org', 'pkg', 'ClassA']
        'com.org.Outer$Inner' -> ['com', 'org', 'Outer.Inner']
        """
        segments = fqn.strip().split(".")
        if not segments:
            return [fqn]
        segments[-1] = segments[-1].replace("$", ".")
        return segments

    @staticmethod
    def _ensure_folder_path(
            root: CodeChartaNode,
            path_segments: List[str],
    ) -> CodeChartaNode:
        """Create or retrieve folder nodes for path."""
        current = root
        for segment in path_segments:
            child = next(
                (c for c in current.children
                 if c.name == segment and c.type == "Folder"),
                None
            )
            if child is None:
                child = CodeChartaNode(name=segment, type="Folder")
                current.children.append(child)
            current = child
        return current

    @staticmethod
    def _add_class_node(
            root: CodeChartaNode,
            fqn: str,
            attributes: Dict[str, Any],
    ) -> str:
        """Add class as File node in tree.

        Returns:
            Absolute CodeCharta path (e.g., '/com/org/pkg/ClassA')
        """
        path_segments = CodeChartaConverter._parse_class_path(fqn)

        if len(path_segments) == 1:
            folder_segments: List[str] = []
            class_name = path_segments[0]
        else:
            folder_segments = path_segments[:-1]
            class_name = path_segments[-1]

        parent = CodeChartaConverter._ensure_folder_path(root, folder_segments)

        file_node = next(
            (c for c in parent.children
             if c.name == class_name and c.type == "File"),
            None
        )

        if file_node is None:
            file_node = CodeChartaNode(
                name=class_name,
                type="File",
                attributes=attributes,
            )
            parent.children.append(file_node)
        else:
            file_node.attributes.update(attributes)

        return "/" + "/".join(path_segments)

    @staticmethod
    def _convert_edges(
            edges: List[Dict[str, Any]],
            node_id_to_path: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Convert internal edges to CodeCharta format."""
        cc_edges: List[Dict[str, Any]] = []

        for edge in edges:
            src_id: str = edge.get("from_id") or edge.get("from") or ""
            tgt_id: str = edge.get("to_id") or edge.get("to") or ""

            if not src_id or not tgt_id:
                continue

            src_path = node_id_to_path.get(src_id)
            tgt_path = node_id_to_path.get(tgt_id)

            if not src_path or not tgt_path:
                continue  # External edge

            cc_edges.append({
                "fromNodeName": src_path,
                "toNodeName": tgt_path,
                "attributes": {
                    "weight": int(edge.get("weight", 1))
                }
            })

        return cc_edges


# Convenience function
def convert_file(
        input_path: str,
        output_path: str,
        project_name: Optional[str] = None,
) -> None:
    """Convert graph.json to codecharta.json."""
    CodeChartaConverter.convert_file(input_path, output_path, project_name)