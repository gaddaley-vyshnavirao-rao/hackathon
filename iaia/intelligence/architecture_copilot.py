from __future__ import annotations

from iaia.models import AnalysisResult


QUESTIONS = [
    'What are the top architecture risks?',
    'Which components have the highest blast radius?',
    'What should I modernize first?',
    'What architecture pattern fits this project?',
    'Where are the circular dependencies?',
]


class ArchitectureCopilot:
    """Answer predefined questions from grounded analysis data only."""

    def answer(self, question: str, result: AnalysisResult) -> str:
        if question == QUESTIONS[0]:
            risks = [f'{f.severity.upper()}: {f.title} ({f.file_path})' for f in result.findings[:5]]
            return 'Top risks from static findings: ' + (', '.join(risks) if risks else 'No findings were detected.') + '. Validate each indicator with an engineer.'
        if question == QUESTIONS[1]:
            graph = result.module_risks
            ranked = sorted(graph.values(), key=lambda risk: (risk.blast_radius_size, risk.score), reverse=True)[:3]
            return 'Highest potential blast radius: ' + (', '.join(f'{risk.module} ({risk.blast_radius_size} connected components)' for risk in ranked) if ranked else 'No dependency graph components are available.') + '. Graph reachability is potential impact, not confirmed operational impact.'
        if question == QUESTIONS[2]:
            actions = result.modernization[:3]
            return 'Modernize first: ' + ('; '.join(f'{action.phase}: {action.title}' for action in actions) if actions else 'No modernization actions were generated.') + '.'
        if question == QUESTIONS[3]:
            if result.cycles:
                return 'A layered modular architecture with dependency inversion fits best: the current graph contains circular dependencies, so shared contracts and adapter boundaries should be introduced before migration.'
            if result.dependencies:
                return 'A modular layered architecture fits the observed internal dependencies. Keep domain responsibilities separate from infrastructure adapters and review dependency direction.'
            return 'The project is currently loosely connected. A modular architecture with explicit interfaces would provide a practical foundation.'
        if question == QUESTIONS[4]:
            return 'Circular dependencies detected: ' + (', '.join(' -> '.join(cycle) for cycle in result.cycles) if result.cycles else 'none detected.')
        return 'Choose one of the predefined architecture questions.'
