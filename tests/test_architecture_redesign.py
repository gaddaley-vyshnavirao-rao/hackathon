import networkx as nx
from iaia.intelligence.architecture_redesign import ArchitectureRedesignEngine
def test_cycle_gets_boundary_proposal():
 g=nx.DiGraph([('a','b'),('b','a')])
 proposals=ArchitectureRedesignEngine().propose({'summary':'x'},g,[])
 assert any('circular' in p.title.lower() for p in proposals)
