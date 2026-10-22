from iaia.models import Recommendation
class AIRecommendationEngine:
    def generate(self, findings, graph, ai_enabled=False):
        out=[]
        for f in findings:
            if f.category=='code-execution': action='Replace dynamic evaluation with a constrained parser or explicit dispatch.'; priority='urgent'
            elif f.category=='secret-management': action='Remove the value, rotate it, and load credentials from a secret manager.'; priority='urgent'
            elif f.category=='command-execution': action='Avoid shell strings; use argument lists, allowlists, and validated inputs.'; priority='high'
            elif f.category=='deserialization': action='Use a safe schema-based format and validate untrusted input.'; priority='high'
            elif f.category=='architecture': action='Split the module around cohesive responsibilities and define interfaces.'; priority='medium'
            else: action='Handle specific exceptions and add observable failure paths.'; priority='medium'
            out.append(Recommendation(finding_title=f.title, discovered=f.explanation, evidence=f.evidence, why_it_matters='The indicator can increase security, reliability, or change risk.', impact='Potentially affects callers and dependents shown by the graph.', corrective_action=action, preventive_measures=['Add secure coding review and automated regression checks.','Document the trust boundary and ownership.'], validation_tests=['Add a focused unit test for safe and unsafe inputs.','Run static checks and review the resulting dependency graph.'], longer_term='Define a small interface and monitor the relevant behavior in production review processes.', priority=priority, rationale=f'Selected from the finding category {f.category}.', confidence=f.confidence, assumptions=['The finding is an indicator and needs engineer confirmation.'], limitations=f.limitations, source='rule-based' if not ai_enabled else 'AI-unverified'))
        return out
