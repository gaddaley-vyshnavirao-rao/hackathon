from __future__ import annotations
import networkx as nx
class ArchitectureModelBuilder:
    def build(self, modules, graph):
        groups={}
        for m in modules:
            layer=m.path.split('/')[0] if '/' in m.path else 'root'
            groups.setdefault(layer,[]).append(m.name)
        hotspots=sorted(graph.nodes, key=lambda n: graph.in_degree(n)+graph.out_degree(n), reverse=True)[:5]
        return {'summary': f'{len(modules)} Python modules grouped into {len(groups)} evidence-based path groups.', 'groups':groups, 'hotspots':hotspots, 'diagram_edges':list(graph.edges), 'inferred': 'Groups use source paths; relationships are AST import evidence only.'}
