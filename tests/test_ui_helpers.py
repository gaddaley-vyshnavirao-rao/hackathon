import networkx as nx

from iaia.ui_helpers import build_dependency_graph


def test_blast_radius_graph_retains_modules_without_dependencies():
    graph = build_dependency_graph(['connected', 'isolated'], [('connected', 'connected')])

    assert graph.has_node('isolated')
    assert graph.has_node('connected')
    assert isinstance(graph, nx.DiGraph)
