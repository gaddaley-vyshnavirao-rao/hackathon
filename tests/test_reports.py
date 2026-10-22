from iaia.models import AnalysisResult
from iaia.reporting.report_generator import ReportGenerator
def test_reports():
 r=AnalysisResult(analysis_id='1',project_name='x',root='.')
 assert 'x' in ReportGenerator().json(r) and '<h1>' in ReportGenerator().html(r)
