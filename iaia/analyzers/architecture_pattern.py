from __future__ import annotations

import networkx as nx
from iaia.models import ArchitecturePattern, ModuleInfo


class ArchitecturePatternDetector:
    """Infer a broad architecture pattern from static project organization signals."""

    def detect(self, modules: list[ModuleInfo], graph: nx.DiGraph) -> ArchitecturePattern:
        paths = [module.path.lower().replace('\\', '/') for module in modules]
        names = ' '.join(paths + [module.name.lower() for module in modules])
        layer_terms = {'controller', 'controllers', 'service', 'services', 'repository', 'repositories', 'model', 'models', 'view', 'views', 'domain', 'adapter', 'adapters'}
        event_terms = {'event', 'events', 'broker', 'queue', 'kafka', 'celery', 'pubsub', 'publish', 'subscribe', 'consumer', 'producer'}
        client_server_terms = {'client', 'server', 'api', 'route', 'routes', 'endpoint', 'frontend', 'backend'}
        layer_hits = sorted({term for term in layer_terms if term in names})
        event_hits = sorted({term for term in event_terms if term in names})
        client_server_hits = sorted({term for term in client_server_terms if term in names})
        groups = {path.split('/')[0] for path in paths if '/' in path}
        signals = []
        if layer_hits and len(groups) >= 2: signals.append(('layered', len(layer_hits) + len(groups)))
        if event_hits: signals.append(('event-driven', len(event_hits) * 2))
        if client_server_hits and len(groups) >= 2: signals.append(('client-server', len(client_server_hits) + len(groups)))
        density = graph.number_of_edges() / max(graph.number_of_nodes(), 1)
        if len(groups) <= 1 and graph.number_of_nodes() >= 3: signals.append(('monolith', 2 + density))
        if not signals: return ArchitecturePattern(pattern='monolith', confidence=0.55, explanation='Modules are mostly at one level and no stronger folder or dependency pattern was detected.', evidence=['module count', 'folder structure', 'dependency density'])
        signals.sort(key=lambda item: item[1], reverse=True)
        top, strength = signals[0]
        if len(signals) > 1 and signals[1][1] >= strength * 0.75:
            selected = ', '.join(item[0] for item in signals[:2])
            return ArchitecturePattern(pattern='hybrid', confidence=round(min(0.9, 0.55 + strength / 30), 2), explanation=f'The project combines strong signals for {selected}; static evidence does not support one dominant pattern.', evidence=layer_hits + event_hits + client_server_hits + [f'{len(groups)} top-level folder groups'])
        confidence = min(0.95, 0.55 + strength / 20)
        evidence = layer_hits if top == 'layered' else event_hits if top == 'event-driven' else client_server_hits if top == 'client-server' else [f'{len(groups)} top-level folder groups', f'{graph.number_of_edges()} dependency edges']
        return ArchitecturePattern(pattern=top, confidence=round(confidence, 2), explanation=f'The classification is based on {top} signals found in folder/module organization and dependency topology.', evidence=evidence)
