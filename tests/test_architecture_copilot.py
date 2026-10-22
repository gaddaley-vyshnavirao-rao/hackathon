from iaia.intelligence.architecture_copilot import ArchitectureCopilot, QUESTIONS
from iaia.models import AnalysisResult, ModernizationAction, ModuleRisk


def test_copilot_answers_from_analysis_context():
    result = AnalysisResult(
        analysis_id='test', project_name='demo', root='.', dependencies=[('a', 'b')],
        cycles=[['a', 'b']], modernization=[ModernizationAction(phase='1', title='Reduce risk', priority='high', evidence='finding', reason='risk', steps=['fix'], dependencies=[], validation=['test'], rollback='revert', benefits=['safer'], uncertainty='review')],
        module_risks={'a': ModuleRisk(module='a', score=60, status='red', finding_penalty=25, blast_radius_size=1, dependency_count=1, explanation='static')},
    )

    answer = ArchitectureCopilot().answer(QUESTIONS[1], result)

    assert 'a (1 connected components)' in answer
