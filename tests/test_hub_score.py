"""Tests for hubScore metric calculator."""

import pytest

from complexity_visualizer.core.models import Graph, Node, Edge
from complexity_visualizer.core.metrics.calculators.degrees import HubScoreCalculator
from complexity_visualizer.core.metrics.base import MetricContext


def create_test_context(nodes, edges, fan_in, fan_out):
    """Helper to create MetricContext with cached fanIn and fanOut."""
    graph = Graph(nodes=nodes, edges=edges)
    node_index = {n.id: i for i, n in enumerate(nodes)}
    adjacency_list = [[] for _ in nodes]
    for edge in edges:
        from_idx = node_index[edge.from_id]
        to_idx = node_index[edge.to_id]
        adjacency_list[from_idx].append(to_idx)

    context = MetricContext(
        graph=graph,
        adjacency_list=adjacency_list,
        node_index=node_index,
        n_nodes=len(nodes),
        cache={"fanIn": fan_in, "fanOut": fan_out},
        source_metrics=None,
    )
    return context


def test_hub_score_pure_consumer():
    """Test hubScore for a pure consumer (fanIn=0, fanOut=5).

    A class that only depends on others but nothing depends on it.
    This should have hubScore = 0 (no hub).
    """
    nodes = [Node(id="Consumer")]
    context = create_test_context(
        nodes=nodes,
        edges=[],
        fan_in=[0],
        fan_out=[5],
    )

    calculator = HubScoreCalculator()
    result = calculator.calculate(context)

    assert result == [0], "Pure consumer should have hubScore = 0"


def test_hub_score_pure_provider():
    """Test hubScore for a pure provider (fanIn=10, fanOut=0).

    A class that many others depend on but it has no dependencies.
    This should have hubScore = 0 (no hub).
    """
    nodes = [Node(id="Provider")]
    context = create_test_context(
        nodes=nodes,
        edges=[],
        fan_in=[10],
        fan_out=[0],
    )

    calculator = HubScoreCalculator()
    result = calculator.calculate(context)

    assert result == [0], "Pure provider should have hubScore = 0"


def test_hub_score_god_class():
    """Test hubScore for a God class (fanIn=8, fanOut=6).

    A class that both:
    - Is heavily depended upon (fanIn=8)
    - Depends on many things (fanOut=6)

    This is the crossroads pattern - a bottleneck.
    hubScore = 8 × 6 = 48
    """
    nodes = [Node(id="GodClass")]
    context = create_test_context(
        nodes=nodes,
        edges=[],
        fan_in=[8],
        fan_out=[6],
    )

    calculator = HubScoreCalculator()
    result = calculator.calculate(context)

    assert result == [48], "God class should have hubScore = 48 (8 × 6)"


def test_hub_score_minimal():
    """Test hubScore for a minimal connection (fanIn=1, fanOut=1).

    A class with minimal connections in both directions.
    hubScore = 1 × 1 = 1 (non-issue)
    """
    nodes = [Node(id="Simple")]
    context = create_test_context(
        nodes=nodes,
        edges=[],
        fan_in=[1],
        fan_out=[1],
    )

    calculator = HubScoreCalculator()
    result = calculator.calculate(context)

    assert result == [1], "Minimal connections should have hubScore = 1"


def test_hub_score_multiple_nodes():
    """Test hubScore for multiple nodes with different patterns."""
    nodes = [
        Node(id="Leaf"),  # fanIn=5, fanOut=0 → hubScore=0
        Node(id="Orchestrator"),  # fanIn=0, fanOut=10 → hubScore=0
        Node(id="GodClass"),  # fanIn=10, fanOut=8 → hubScore=80
        Node(id="Helper"),  # fanIn=3, fanOut=2 → hubScore=6
    ]

    context = create_test_context(
        nodes=nodes,
        edges=[],
        fan_in=[5, 0, 10, 3],
        fan_out=[0, 10, 8, 2],
    )

    calculator = HubScoreCalculator()
    result = calculator.calculate(context)

    assert result == [0, 0, 80, 6], (
        "Multiple nodes should have correct hubScores: "
        "Leaf=0, Orchestrator=0, GodClass=80, Helper=6"
    )


def test_hub_score_zero_connections():
    """Test hubScore for a node with no connections."""
    nodes = [Node(id="Isolated")]
    context = create_test_context(
        nodes=nodes,
        edges=[],
        fan_in=[0],
        fan_out=[0],
    )

    calculator = HubScoreCalculator()
    result = calculator.calculate(context)

    assert result == [0], "Isolated node should have hubScore = 0"


def test_hub_score_calculator_dependencies():
    """Test that HubScoreCalculator declares correct dependencies."""
    calculator = HubScoreCalculator()

    assert calculator.dependencies == {"fanIn", "fanOut"}, (
        "HubScoreCalculator should depend on fanIn and fanOut"
    )


def test_hub_score_calculator_name():
    """Test that HubScoreCalculator has correct name."""
    calculator = HubScoreCalculator()
    assert calculator.name == "hubScore"
