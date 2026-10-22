import networkx as nx

from iaia.analyzers.architecture_pattern import ArchitecturePatternDetector
from iaia.models import ModuleInfo


def test_layered_pattern_detection_has_confidence_and_explanation():
    modules = [
        ModuleInfo(name='controllers.api', path='controllers/api.py'),
        ModuleInfo(name='services.orders', path='services/orders.py'),
        ModuleInfo(name='repositories.orders', path='repositories/orders.py'),
    ]
    graph = nx.DiGraph([('controllers.api', 'services.orders'), ('services.orders', 'repositories.orders')])

    result = ArchitecturePatternDetector().detect(modules, graph)

    assert result.pattern == 'layered'
    assert 0 < result.confidence <= 1
    assert result.explanation
    assert result.evidence
