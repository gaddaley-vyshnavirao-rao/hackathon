from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from iaia.models import AnalysisResult


class PDFReportGenerator:
    """Generate a readable PDF from the structured analysis result."""

    def generate(self, result: AnalysisResult) -> bytes:
        output = BytesIO()
        document = SimpleDocTemplate(output, pagesize=letter, rightMargin=.65 * inch, leftMargin=.65 * inch, topMargin=.6 * inch, bottomMargin=.6 * inch)
        styles = getSampleStyleSheet()
        story = [Paragraph(f'IAIA Architecture Analysis - {escape(result.project_name)}', styles['Title']), Spacer(1, 12)]

        def section(title, body):
            story.append(Paragraph(escape(title), styles['Heading2']))
            for line in body:
                story.append(Paragraph(escape(str(line)), styles['BodyText']))
                story.append(Spacer(1, 5))

        summary = result.executive_summary
        section('Executive Summary', [summary.business_summary, summary.technical_summary] if summary else ['No executive summary is available.'])
        score = result.health_score
        section('Architecture Score', [f'Overall: {score.overall}/100; maintainability: {score.maintainability}/100; security: {score.security}/100; coupling: {score.coupling}/100; complexity: {score.complexity}/100.'] if score else ['No architecture score is available.'])
        section('Findings', [f'{finding.severity.upper()}: {finding.title} - {finding.file_path}:{finding.line or "?"}. Evidence: {finding.evidence}. Recommendation: {finding.recommendation or "Review with an engineer."}' for finding in result.findings] or ['No findings were detected.'])
        highlights = sorted(result.module_risks.values(), key=lambda risk: (risk.blast_radius_size, risk.score), reverse=True)[:5]
        section('Blast Radius Highlights', [f'{risk.module}: potential blast radius {risk.blast_radius_size}, risk score {risk.score}, status {risk.status}.' for risk in highlights] or ['No blast-radius highlights are available.'])
        section('Modernization Roadmap', [f'{action.phase}: {action.title}. Dependencies: {", ".join(action.dependencies) or "none"}.' for action in result.modernization] or ['No modernization actions were generated.'])
        section('Recommendations', [f'{recommendation.priority}: {recommendation.corrective_action}' for recommendation in result.recommendations] or ['No recommendations were generated.'])
        section('Limitations', result.limitations)
        document.build(story)
        return output.getvalue()
