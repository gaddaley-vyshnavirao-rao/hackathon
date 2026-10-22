from __future__ import annotations
import networkx as nx
class BlastRadiusAnalyzer:
    def __init__(self, graph): self.graph=graph
    def analyze(self, node):
        if not self.graph.has_node(node):
            raise KeyError(node)
        deps=sorted(self.graph.successors(node)); dependents=sorted(self.graph.predecessors(node))
        affected={}; paths={}
        for other in self.graph.nodes:
            if other==node: continue
            p=list(nx.all_simple_paths(self.graph, node, other)) if nx.has_path(self.graph,node,other) else []
            reverse=list(nx.all_simple_paths(self.graph, other, node)) if nx.has_path(self.graph,other,node) else []
            if p or reverse:
                direction='dependency' if p else 'dependent'
                chosen=p or reverse; depth=min(len(x)-1 for x in chosen)
                affected[other]={'direction':direction,'depth':depth,'reason':f'{other} is reachable as a {direction} through static import edges.'}
                paths[other]=chosen[:5]
        score=min(100, len(dependents)*20+len(affected)*10+len(deps)*5)
        return {'node':node,'direct_dependencies':deps,'direct_dependents':dependents,'affected':affected,'paths':paths,'impact_depth':max((x['depth'] for x in affected.values()),default=0),'impact_score':score,'explanation':'Score is an explainable graph heuristic, not confirmed operational impact.'}
