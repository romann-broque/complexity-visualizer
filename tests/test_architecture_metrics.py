"""Tests for architecture metrics (abstractness and distanceFromMainSequence)."""

import pytest

from complexity_visualizer.core.metrics.base import MetricContext
from complexity_visualizer.core.metrics.calculators.architecture import (
    AbstractnessCalculator,
    DistanceFromMainSequenceCalculator,
)
from complexity_visualizer.core.models import Edge, Graph, Node


def test_abstractness_mixed_package():
    """Package with 2 interfaces and 3 concrete classes -> abstractness = 0.4"""
    nodes = [
        Node(id="com.example.InterfaceA", type="class"),
        Node(id="com.example.InterfaceB", type="class"),
        Node(id="com.example.ConcreteA", type="class"),
        Node(id="com.example.ConcreteB", type="class"),
        Node(id="com.example.ConcreteC", type="class"),
    ]
    graph = Graph(nodes=nodes, edges=[])

    source_metrics = {
        "com.example.InterfaceA": {"is_abstract": 1, "loc": 10, "complexity": 1},
        "com.example.InterfaceB": {"is_abstract": 1, "loc": 15, "complexity": 1},
        "com.example.ConcreteA": {"is_abstract": 0, "loc": 50, "complexity": 5},
        "com.example.ConcreteB": {"is_abstract": 0, "loc": 40, "complexity": 3},
        "com.example.ConcreteC": {"is_abstract": 0, "loc": 60, "complexity": 7},
    }

    context = MetricContext(
        graph=graph,
        adjacency_list=[[], [], [], [], []],
        node_index={n.id: i for i, n in enumerate(nodes)},
        n_nodes=5,
        source_metrics=source_metrics,
    )

    calculator = AbstractnessCalculator()
    results = calculator.calculate(context)

    # All classes in the same package should have the same abstractness value
    expected = 2 / 5  # 2 abstract out of 5 total = 0.4
    for result in results:
        assert result == pytest.approx(expected)


def test_abstractness_all_concrete():
    """Package with 0 interfaces -> abstractness = 0.0"""
    nodes = [
        Node(id="com.example.ConcreteA", type="class"),
        Node(id="com.example.ConcreteB", type="class"),
        Node(id="com.example.ConcreteC", type="class"),
    ]
    graph = Graph(nodes=nodes, edges=[])

    source_metrics = {
        "com.example.ConcreteA": {"is_abstract": 0, "loc": 50, "complexity": 5},
        "com.example.ConcreteB": {"is_abstract": 0, "loc": 40, "complexity": 3},
        "com.example.ConcreteC": {"is_abstract": 0, "loc": 60, "complexity": 7},
    }

    context = MetricContext(
        graph=graph,
        adjacency_list=[[], [], []],
        node_index={n.id: i for i, n in enumerate(nodes)},
        n_nodes=3,
        source_metrics=source_metrics,
    )

    calculator = AbstractnessCalculator()
    results = calculator.calculate(context)

    # All concrete classes
    for result in results:
        assert result == 0.0


def test_abstractness_all_abstract():
    """Package with only interfaces -> abstractness = 1.0"""
    nodes = [
        Node(id="com.example.InterfaceA", type="class"),
        Node(id="com.example.InterfaceB", type="class"),
        Node(id="com.example.InterfaceC", type="class"),
    ]
    graph = Graph(nodes=nodes, edges=[])

    source_metrics = {
        "com.example.InterfaceA": {"is_abstract": 1, "loc": 10, "complexity": 1},
        "com.example.InterfaceB": {"is_abstract": 1, "loc": 15, "complexity": 1},
        "com.example.InterfaceC": {"is_abstract": 1, "loc": 12, "complexity": 1},
    }

    context = MetricContext(
        graph=graph,
        adjacency_list=[[], [], []],
        node_index={n.id: i for i, n in enumerate(nodes)},
        n_nodes=3,
        source_metrics=source_metrics,
    )

    calculator = AbstractnessCalculator()
    results = calculator.calculate(context)

    # All abstract/interfaces
    for result in results:
        assert result == 1.0


def test_abstractness_multiple_packages():
    """Classes in different packages should have different abstractness values"""
    nodes = [
        Node(id="com.example.pkg1.InterfaceA", type="class"),
        Node(id="com.example.pkg1.ConcreteA", type="class"),
        Node(id="com.example.pkg2.ConcreteB", type="class"),
        Node(id="com.example.pkg2.ConcreteC", type="class"),
    ]
    graph = Graph(nodes=nodes, edges=[])

    source_metrics = {
        "com.example.pkg1.InterfaceA": {"is_abstract": 1, "loc": 10, "complexity": 1},
        "com.example.pkg1.ConcreteA": {"is_abstract": 0, "loc": 50, "complexity": 5},
        "com.example.pkg2.ConcreteB": {"is_abstract": 0, "loc": 40, "complexity": 3},
        "com.example.pkg2.ConcreteC": {"is_abstract": 0, "loc": 60, "complexity": 7},
    }

    context = MetricContext(
        graph=graph,
        adjacency_list=[[], [], [], []],
        node_index={n.id: i for i, n in enumerate(nodes)},
        n_nodes=4,
        source_metrics=source_metrics,
    )

    calculator = AbstractnessCalculator()
    results = calculator.calculate(context)

    # pkg1 has 1 abstract out of 2 = 0.5
    assert results[0] == pytest.approx(0.5)
    assert results[1] == pytest.approx(0.5)

    # pkg2 has 0 abstract out of 2 = 0.0
    assert results[2] == 0.0
    assert results[3] == 0.0


def test_distance_zone_of_pain():
    """Package with abstractness=0.0, instability=0.0 -> distance = 1.0 (zone of pain)"""
    nodes = [Node(id="com.example.ClassA", type="class")]
    graph = Graph(nodes=nodes, edges=[])

    context = MetricContext(
        graph=graph,
        adjacency_list=[[]],
        node_index={"com.example.ClassA": 0},
        n_nodes=1,
        cache={"abstractness": [0.0], "instability": [0.0]},
    )

    calculator = DistanceFromMainSequenceCalculator()
    results = calculator.calculate(context)

    # distance = |0.0 + 0.0 - 1| = 1.0
    assert results[0] == pytest.approx(1.0)


def test_distance_ideal_abstract_stable():
    """Package with abstractness=1.0, instability=0.0 -> distance = 0.0 (ideal)"""
    nodes = [Node(id="com.example.Interface", type="class")]
    graph = Graph(nodes=nodes, edges=[])

    context = MetricContext(
        graph=graph,
        adjacency_list=[[]],
        node_index={"com.example.Interface": 0},
        n_nodes=1,
        cache={"abstractness": [1.0], "instability": [0.0]},
    )

    calculator = DistanceFromMainSequenceCalculator()
    results = calculator.calculate(context)

    # distance = |1.0 + 0.0 - 1| = 0.0
    assert results[0] == pytest.approx(0.0)


def test_distance_ideal_balanced():
    """Package with abstractness=0.5, instability=0.5 -> distance = 0.0 (ideal)"""
    nodes = [Node(id="com.example.ClassA", type="class")]
    graph = Graph(nodes=nodes, edges=[])

    context = MetricContext(
        graph=graph,
        adjacency_list=[[]],
        node_index={"com.example.ClassA": 0},
        n_nodes=1,
        cache={"abstractness": [0.5], "instability": [0.5]},
    )

    calculator = DistanceFromMainSequenceCalculator()
    results = calculator.calculate(context)

    # distance = |0.5 + 0.5 - 1| = 0.0
    assert results[0] == pytest.approx(0.0)


def test_distance_ideal_concrete_unstable():
    """Package with abstractness=0.0, instability=1.0 -> distance = 0.0 (ideal)"""
    nodes = [Node(id="com.example.Utility", type="class")]
    graph = Graph(nodes=nodes, edges=[])

    context = MetricContext(
        graph=graph,
        adjacency_list=[[]],
        node_index={"com.example.Utility": 0},
        n_nodes=1,
        cache={"abstractness": [0.0], "instability": [1.0]},
    )

    calculator = DistanceFromMainSequenceCalculator()
    results = calculator.calculate(context)

    # distance = |0.0 + 1.0 - 1| = 0.0
    assert results[0] == pytest.approx(0.0)


def test_distance_zone_of_uselessness():
    """Package with abstractness=1.0, instability=1.0 -> distance = 1.0 (zone of uselessness)"""
    nodes = [Node(id="com.example.UnusedInterface", type="class")]
    graph = Graph(nodes=nodes, edges=[])

    context = MetricContext(
        graph=graph,
        adjacency_list=[[]],
        node_index={"com.example.UnusedInterface": 0},
        n_nodes=1,
        cache={"abstractness": [1.0], "instability": [1.0]},
    )

    calculator = DistanceFromMainSequenceCalculator()
    results = calculator.calculate(context)

    # distance = |1.0 + 1.0 - 1| = 1.0
    assert results[0] == pytest.approx(1.0)


def test_abstractness_no_source_metrics():
    """When source metrics are not available, return 0.0 for all nodes"""
    nodes = [
        Node(id="com.example.ClassA", type="class"),
        Node(id="com.example.ClassB", type="class"),
    ]
    graph = Graph(nodes=nodes, edges=[])

    context = MetricContext(
        graph=graph,
        adjacency_list=[[], []],
        node_index={n.id: i for i, n in enumerate(nodes)},
        n_nodes=2,
        source_metrics=None,
    )

    calculator = AbstractnessCalculator()
    results = calculator.calculate(context)

    # Without source metrics, should return 0.0
    assert all(r == 0.0 for r in results)
