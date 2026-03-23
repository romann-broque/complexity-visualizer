"""Tests for class-level cycle detection and bidirectional links."""

import pytest

from complexity_visualizer.core.metrics.base import MetricContext
from complexity_visualizer.core.metrics.calculators.cycles import (
    CycleParticipationCalculator,
)
from complexity_visualizer.core.metrics.calculators.coupling import (
    BidirectionalLinksCalculator,
)
from complexity_visualizer.core.models import Edge, Graph, Node


def create_test_graph(nodes: list[str], edges: list[tuple[str, str]]) -> Graph:
    """Helper to create a test graph from node names and edge pairs."""
    node_objects = [Node(id=name) for name in nodes]

    edge_objects = [Edge(from_id=src, to_id=tgt) for src, tgt in edges]

    return Graph(nodes=node_objects, edges=edge_objects)


def create_context(graph: Graph) -> MetricContext:
    """Helper to create a MetricContext from a graph."""
    # Build node_index mapping
    node_index = {node.id: i for i, node in enumerate(graph.nodes)}

    # Build adjacency list
    adjacency_list = [[] for _ in graph.nodes]
    for edge in graph.edges:
        source_idx = node_index[edge.from_id]
        target_idx = node_index[edge.to_id]
        adjacency_list[source_idx].append(target_idx)

    return MetricContext(
        graph=graph,
        adjacency_list=adjacency_list,
        node_index=node_index,
        n_nodes=len(graph.nodes),
    )


class TestCycleParticipation:
    """Test suite for class-level cycle participation."""

    def test_cycle_between_two_classes(self):
        """Test that a simple cycle between two classes is detected."""
        graph = create_test_graph(
            nodes=["ClassA", "ClassB"],
            edges=[("ClassA", "ClassB"), ("ClassB", "ClassA")],
        )
        context = create_context(graph)

        calculator = CycleParticipationCalculator()
        result = calculator.calculate(context)

        assert result == [2, 2], "Both classes should be in a cycle of size 2"

    def test_cycle_between_three_classes(self):
        """Test that a cycle among three classes is detected."""
        graph = create_test_graph(
            nodes=["ClassA", "ClassB", "ClassC"],
            edges=[("ClassA", "ClassB"), ("ClassB", "ClassC"), ("ClassC", "ClassA")],
        )
        context = create_context(graph)

        calculator = CycleParticipationCalculator()
        result = calculator.calculate(context)

        assert result == [3, 3, 3], "All three classes should be in a cycle of size 3"

    def test_packages_in_cycle_ignored(self):
        """Test that cycles at package level don't affect class metrics."""
        graph = create_test_graph(
            nodes=["com.example", "com.other", "ClassA", "ClassB"],
            edges=[
                ("com.example", "com.other"),  # Package-level cycle
                ("com.other", "com.example"),
                ("ClassA", "ClassB"),  # No class-level cycle
            ],
        )
        context = create_context(graph)

        calculator = CycleParticipationCalculator()
        result = calculator.calculate(context)

        # Packages (indices 0, 1) should have 0 (not in class-level cycles)
        # Classes (indices 2, 3) should have 0 (no cycle between them)
        assert result == [0, 0, 0, 0], "Package cycles should not affect class metrics"

    def test_mixed_graph_with_class_cycle(self):
        """Test a mixed graph where classes are in a cycle but packages are not."""
        graph = create_test_graph(
            nodes=["com.example", "ClassA", "ClassB"],
            edges=[
                ("ClassA", "ClassB"),
                ("ClassB", "ClassA"),
                ("ClassA", "com.example"),  # Class depends on package
            ],
        )
        context = create_context(graph)

        calculator = CycleParticipationCalculator()
        result = calculator.calculate(context)

        # Package at index 0: not in class cycle
        # ClassA and ClassB at indices 1, 2: in cycle of size 2
        assert result == [0, 2, 2], (
            "Only classes should participate in class-level cycles"
        )

    def test_complex_mixed_graph(self):
        """Test a complex graph with both package and class cycles."""
        graph = create_test_graph(
            nodes=[
                "com.adapter",
                "com.web",  # Packages (cycle at package level)
                "AdapterClass",
                "WebClass",
                "UtilClass",  # Classes
            ],
            edges=[
                # Package-level cycle
                ("com.adapter", "com.web"),
                ("com.web", "com.adapter"),
                # Class-level cycle
                ("AdapterClass", "WebClass"),
                ("WebClass", "AdapterClass"),
                # Additional edges
                ("UtilClass", "AdapterClass"),
            ],
        )
        context = create_context(graph)

        calculator = CycleParticipationCalculator()
        result = calculator.calculate(context)

        # Packages (0, 1): 0 (not classes)
        # AdapterClass and WebClass (2, 3): cycle of 2
        # UtilClass (4): 0 (not in cycle)
        assert result == [0, 0, 2, 2, 0], "Only class-level cycles should be detected"

    def test_no_cycles(self):
        """Test that a DAG has no cycles."""
        graph = create_test_graph(
            nodes=["ClassA", "ClassB", "ClassC"],
            edges=[("ClassA", "ClassB"), ("ClassB", "ClassC")],
        )
        context = create_context(graph)

        calculator = CycleParticipationCalculator()
        result = calculator.calculate(context)

        assert result == [0, 0, 0], "No cycles should be detected in a DAG"

    def test_self_loop_ignored(self):
        """Test that self-loops are ignored (cycle size = 1)."""
        graph = create_test_graph(
            nodes=["ClassA", "ClassB"],
            edges=[
                ("ClassA", "ClassA"),  # Self-loop
                ("ClassA", "ClassB"),
            ],
        )
        context = create_context(graph)

        calculator = CycleParticipationCalculator()
        result = calculator.calculate(context)

        assert result == [0, 0], "Self-loops should be ignored (SCC size 1)"


class TestBidirectionalLinks:
    """Test suite for class-level bidirectional link detection."""

    def test_simple_bidirectional_link(self):
        """Test that a simple bidirectional link between classes is detected."""
        graph = create_test_graph(
            nodes=["ClassA", "ClassB"],
            edges=[("ClassA", "ClassB"), ("ClassB", "ClassA")],
        )
        context = create_context(graph)

        calculator = BidirectionalLinksCalculator()
        result = calculator.calculate(context)

        assert result == [1, 1], "Each class should have 1 bidirectional link"

    def test_multiple_bidirectional_links(self):
        """Test a class with multiple bidirectional links."""
        graph = create_test_graph(
            nodes=["ClassA", "ClassB", "ClassC"],
            edges=[
                ("ClassA", "ClassB"),
                ("ClassB", "ClassA"),
                ("ClassA", "ClassC"),
                ("ClassC", "ClassA"),
            ],
        )
        context = create_context(graph)

        calculator = BidirectionalLinksCalculator()
        result = calculator.calculate(context)

        assert result == [2, 1, 1], "ClassA should have 2 bidirectional links"

    def test_unidirectional_link_not_counted(self):
        """Test that unidirectional dependencies are not counted."""
        graph = create_test_graph(
            nodes=["ClassA", "ClassB"],
            edges=[("ClassA", "ClassB")],  # Only one direction
        )
        context = create_context(graph)

        calculator = BidirectionalLinksCalculator()
        result = calculator.calculate(context)

        assert result == [0, 0], "Unidirectional links should not be counted"

    def test_packages_ignored(self):
        """Test that package nodes are ignored in bidirectional link calculation."""
        graph = create_test_graph(
            nodes=["com.example", "com.other", "ClassA"],
            edges=[
                ("com.example", "com.other"),  # Package bidirectional link
                ("com.other", "com.example"),
                ("ClassA", "com.example"),
            ],
        )
        context = create_context(graph)

        calculator = BidirectionalLinksCalculator()
        result = calculator.calculate(context)

        assert result == [0, 0, 0], "Package bidirectional links should be ignored"

    def test_class_to_package_bidirectional_ignored(self):
        """Test that class↔package bidirectional links are ignored."""
        graph = create_test_graph(
            nodes=["com.example", "ClassA"],
            edges=[("ClassA", "com.example"), ("com.example", "ClassA")],
        )
        context = create_context(graph)

        calculator = BidirectionalLinksCalculator()
        result = calculator.calculate(context)

        # Package at index 0: ignored (not a class)
        # ClassA at index 1: 0 (bidirectional link is with a package, not a class)
        assert result == [0, 0], (
            "Class-to-package bidirectional links should be ignored"
        )

    def test_mixed_graph_only_class_bidirectional_counted(self):
        """Test that only class-to-class bidirectional links are counted."""
        graph = create_test_graph(
            nodes=["com.pkg", "ClassA", "ClassB", "ClassC"],
            edges=[
                # Package involved in bidirectional
                ("com.pkg", "ClassA"),
                ("ClassA", "com.pkg"),
                # Class-to-class bidirectional
                ("ClassA", "ClassB"),
                ("ClassB", "ClassA"),
                # Unidirectional
                ("ClassA", "ClassC"),
            ],
        )
        context = create_context(graph)

        calculator = BidirectionalLinksCalculator()
        result = calculator.calculate(context)

        # com.pkg (0): ignored
        # ClassA (1): 1 bidirectional link (with ClassB only)
        # ClassB (2): 1 bidirectional link (with ClassA)
        # ClassC (3): 0 bidirectional links
        assert result == [0, 1, 1, 0], (
            "Only class-to-class bidirectional links should count"
        )
