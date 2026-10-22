import networkx as nx

from iaia.analyzers.module_risk import ModuleRiskEngine
from iaia.models import Finding


def test_module_risk_uses_findings_blast_radius_and_dependencies():
    graph = nx.DiGraph([('a', 'b'), ('b', 'c')])
    finding = Finding(title='Risk', category='security', severity='high', file_path='a.py', evidence='x', explanation='x', confidence=.9, limitations='indicator')

    risks = ModuleRiskEngine().calculate(graph, [finding])

    assert risks['a'].finding_penalty == 25
    assert risks['a'].blast_radius_size == 2
    assert risks['a'].dependency_count == 1
    assert risks['a'].status == 'red'
    assert risks['c'].status == 'green'
