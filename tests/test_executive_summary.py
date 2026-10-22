from iaia.intelligence.executive_summary import ExecutiveSummaryGenerator
from iaia.models import Finding


def test_executive_summary_prioritizes_critical_findings():
    finding = Finding(title='Unsafe operation', category='security', severity='high', file_path='config.py', line=4, evidence='eval', explanation='indicator', confidence=.9, limitations='requires review')
    summary = ExecutiveSummaryGenerator().generate(['config.py'], 1, 0, [], [finding], [], [])

    assert summary.project_size == '1 Python files, 1 modules, and 0 internal dependencies.'
    assert summary.architecture_type == 'Standalone or loosely connected Python modules.'
    assert summary.critical_findings == ['Unsafe operation (config.py:4)']
    assert 'high-risk' in summary.modernization_priority
