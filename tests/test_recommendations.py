from iaia.intelligence.recommendation_engine import AIRecommendationEngine
from iaia.models import Finding
import networkx as nx
def test_rule_recommendation():
 f=Finding(title='Use of eval',category='code-execution',severity='high',file_path='x.py',evidence='eval',explanation='risk',confidence=.9,limitations='indicator')
 assert 'parser' in AIRecommendationEngine().generate([f],nx.DiGraph())[0].corrective_action
