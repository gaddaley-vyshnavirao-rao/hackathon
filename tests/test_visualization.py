from iaia.models import ModernizationAction
from iaia.visualization import build_modernization_roadmap


def test_modernization_roadmap_contains_phase_milestones_and_dependencies():
    actions = [
        ModernizationAction(phase='1. Risk reduction', title='Secure inputs', priority='high', evidence='finding', reason='risk', steps=['fix'], dependencies=[], validation=['test'], rollback='revert', benefits=['safer'], uncertainty='review'),
        ModernizationAction(phase='2. Design improvements', title='Define boundaries', priority='medium', evidence='coupling', reason='design', steps=['split'], dependencies=['Secure inputs'], validation=['test'], rollback='revert', benefits=['clearer'], uncertainty='review'),
    ]

    figure = build_modernization_roadmap(actions)

    assert figure.data[0].text == ('1. Risk reduction', '2. Design improvements')
    assert len(figure.data) == 2
