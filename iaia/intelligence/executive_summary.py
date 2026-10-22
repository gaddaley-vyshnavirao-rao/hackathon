from __future__ import annotations

from iaia.models import ExecutiveSummary, Finding, Recommendation, RedesignProposal


class ExecutiveSummaryGenerator:
    """Create a concise, evidence-based summary without external AI calls."""

    def generate(
        self,
        files: list[str],
        modules: int,
        dependencies: int,
        cycles: list[list[str]],
        findings: list[Finding],
        recommendations: list[Recommendation],
        redesign: list[RedesignProposal],
    ) -> ExecutiveSummary:
        size = f'{len(files)} Python files, {modules} modules, and {dependencies} internal dependencies.'
        if cycles:
            architecture_type = 'Modular Python architecture with circular dependency coupling.'
        elif dependencies:
            architecture_type = 'Modular Python architecture with statically observed internal dependencies.'
        else:
            architecture_type = 'Standalone or loosely connected Python modules.'

        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        ordered = sorted(findings, key=lambda finding: (severity_order.get(finding.severity, 4), finding.file_path, finding.line or 0))
        top_risks = [f'{finding.severity.upper()}: {finding.title} in {finding.file_path}' for finding in ordered[:5]]
        critical_findings = [f'{finding.title} ({finding.file_path}:{finding.line or "?"})' for finding in ordered if finding.severity in {'critical', 'high'}][:5]
        improvements = [recommendation.corrective_action for recommendation in recommendations[:5]]
        improvements += [proposal.title for proposal in redesign[:3] if proposal.title not in improvements]

        if any(f.severity == 'critical' for f in findings):
            priority = 'Immediate risk reduction is required before structural modernization.'
        elif any(f.severity == 'high' for f in findings) or cycles:
            priority = 'Prioritize high-risk findings and dependency-boundary improvements.'
        elif findings:
            priority = 'Address the identified findings, then validate incremental design improvements.'
        else:
            priority = 'Continue with baseline testing and controlled architecture evolution.'

        business = f'The project contains {size.lower()} Static analysis identified {len(findings)} indicator(s); engineering review should prioritize safe change and operational continuity.'
        technical = f'The reconstructed design is {architecture_type.lower()} {len(cycles)} circular dependency cycle(s) were detected.'
        return ExecutiveSummary(
            project_size=size,
            architecture_type=architecture_type,
            top_risks=top_risks,
            critical_findings=critical_findings,
            recommended_improvements=improvements,
            modernization_priority=priority,
            business_summary=business,
            technical_summary=technical,
        )
