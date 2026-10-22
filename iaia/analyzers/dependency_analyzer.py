from __future__ import annotations
import networkx as nx
from pathlib import Path
from iaia.models import ModuleInfo

class DependencyAnalyzer:
    def analyze(self, modules: list[ModuleInfo]):
        names={m.name for m in modules}; short={n.rsplit('.',1)[-1]:n for n in names}; graph=nx.DiGraph(); graph.add_nodes_from(names); edges=[]; external={m.name:[] for m in modules}; unresolved=[]
        for m in modules:
            for imp in m.imports:
                candidate = imp.lstrip('.').split('.')[0] if imp.startswith('.') else imp.split('.')[0]
                matches=[n for n in names if n==imp or n.startswith(imp+'.') or n.split('.')[0]==candidate]
                if matches:
                    target=sorted(matches, key=len)[0]; graph.add_edge(m.name,target); edges.append((m.name,target))
                elif not imp.startswith('.') and imp: external[m.name].append(imp)
                elif imp: unresolved.append(f'{m.name} -> {imp}')
        return graph, edges, external, unresolved, [list(c) for c in nx.simple_cycles(graph)]
