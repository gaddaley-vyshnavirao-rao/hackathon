from __future__ import annotations
import networkx as nx


def build_dependency_graph(module_names, dependencies):
    """Build a graph that retains isolated analyzed modules."""
    graph = nx.DiGraph()
    graph.add_nodes_from(module_names)
    graph.add_edges_from(dependencies)
    return graph
