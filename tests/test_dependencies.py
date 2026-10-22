import networkx as nx
from iaia.analyzers.dependency_analyzer import DependencyAnalyzer
from iaia.models import ModuleInfo
def test_edges_and_cycles():
 ms=[ModuleInfo(name='a',path='a.py',imports=['b']),ModuleInfo(name='b',path='b.py',imports=['a'])]
 g,e,_,_,cycles=DependencyAnalyzer().analyze(ms)
 assert set(e)=={('a','b'),('b','a')} and cycles
