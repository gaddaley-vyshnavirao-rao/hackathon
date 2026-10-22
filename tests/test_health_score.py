import networkx as nx

from iaia.analyzers.health_score import ArchitectureHealthEngine
from iaia.models import Finding


def test_health_score_is_deterministic_and_penalizes_risk():
    graph = nx.DiGraph([('a', 'b'), ('b', 'a'), ('b', 'c')])
    finding = Finding(title='Risk', category='security', severity='high', file_path='a.py', evidence='x', explanation='x', confidence=.9, limitations='indicator')

    score = ArchitectureHealthEngine().calculate(graph, [finding], [['a', 'b']])

    assert score.module_count == 3
    assert score.dependency_count == 3
    assert score.circular_dependency_count == 1
    assert score.blast_radius_size == 3
    assert score.security < 100
    assert score.overall == ArchitectureHealthEngine().calculate(graph, [finding], [['a', 'b']]).overall
