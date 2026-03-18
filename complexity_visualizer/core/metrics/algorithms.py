"""Reusable graph algorithms for metric calculations.

This module contains common graph algorithms that can be used by
multiple metric calculators. Extracted here to avoid duplication
and improve testability.
"""

from typing import List, Set


def tarjan_scc(adj: List[List[int]]) -> List[List[int]]:
    """Tarjan's algorithm for strongly connected components.

    Finds all strongly connected components (cycles) in a directed graph.

    Args:
        adj: Adjacency list representation of the graph

    Returns:
        List of SCCs, where each SCC is a list of node indices
    """
    n = len(adj)
    index = 0
    stack = []
    on_stack = [False] * n
    indices = [-1] * n
    lowlink = [0] * n
    sccs = []

    def visit(v: int):
        nonlocal index
        indices[v] = lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack[v] = True

        for w in adj[v]:
            if indices[w] == -1:
                visit(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack[w]:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in range(n):
        if indices[v] == -1:
            visit(v)

    return sccs


def transitive_closure(adj: List[List[int]], start: int) -> Set[int]:
    """Compute transitive closure from a node using BFS.

    Finds all nodes reachable from the start node through any path.

    Args:
        adj: Adjacency list representation of the graph
        start: Starting node index

    Returns:
        Set of all reachable node indices (excluding start itself)
    """
    visited = set()
    queue = [start]
    visited.add(start)

    while queue:
        node = queue.pop(0)
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    visited.discard(start)
    return visited


def compute_in_degrees(adj: List[List[int]]) -> List[int]:
    """Compute in-degree for each node.

    Args:
        adj: Adjacency list representation of the graph

    Returns:
        List of in-degrees (one per node)
    """
    n = len(adj)
    in_deg = [0] * n
    for neighbors in adj:
        for v in neighbors:
            in_deg[v] += 1
    return in_deg


def compute_out_degrees(adj: List[List[int]]) -> List[int]:
    """Compute out-degree for each node.

    Args:
        adj: Adjacency list representation of the graph

    Returns:
        List of out-degrees (one per node)
    """
    return [len(neighbors) for neighbors in adj]
