from iaia.models import AnalysisResult
from iaia.reporting.pdf_generator import PDFReportGenerator


def test_pdf_report_contains_pdf_signature():
    data = PDFReportGenerator().generate(AnalysisResult(analysis_id='pdf-test', project_name='demo', root='.'))

    assert data.startswith(b'%PDF')
    assert len(data) > 500
