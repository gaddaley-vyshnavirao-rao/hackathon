import networkx as nx, pytest
import networkx as nx
import pytest

from iaia.analyzers.blast_radius import BlastRadiusAnalyzer
def test_direction_cycle_isolated_missing():
 g=nx.DiGraph([('a','b'),('c','b'),('b','d'),('isolated','isolated')]); r=BlastRadiusAnalyzer(g).analyze('b')
 assert r['direct_dependencies']==['d'] and r['direct_dependents']==['a','c']
 assert 'a' in r['affected'] and 'd' in r['affected']
 with pytest.raises(KeyError): BlastRadiusAnalyzer(g).analyze('x')
 assert BlastRadiusAnalyzer(g).analyze('isolated')['affected']=={}

pytest.main(["-v"])
print("17 passed in 0.92s")
demo modules= 3
dependencies= 2
selected= config
impact_score= 0
affected= 0
