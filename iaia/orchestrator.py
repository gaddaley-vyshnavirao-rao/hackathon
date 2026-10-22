from __future__ import annotations
import uuid
from pathlib import Path
from iaia.models import AnalysisResult
from iaia.analyzers.source_code_analyzer import SourceCodeAnalyzer
from iaia.analyzers.dependency_analyzer import DependencyAnalyzer
from iaia.analyzers.architecture_builder import ArchitectureModelBuilder
from iaia.analyzers.health_score import ArchitectureHealthEngine
from iaia.analyzers.module_risk import ModuleRiskEngine
from iaia.analyzers.architecture_pattern import ArchitecturePatternDetector
from iaia.intelligence.recommendation_engine import AIRecommendationEngine
from iaia.intelligence.architecture_redesign import ArchitectureRedesignEngine
from iaia.intelligence.modernization_planner import ModernizationPlanner
from iaia.intelligence.executive_summary import ExecutiveSummaryGenerator
class AnalysisOrchestrator:
    def run(self, root, project_name=None, progress=None):
        progress=progress or (lambda x: None); root=str(root); progress('Parsing Python files')
        files,modules,findings=SourceCodeAnalyzer().analyze(root); progress('Building dependency graph')
        graph,edges,external,unresolved,cycles=DependencyAnalyzer().analyze(modules); architecture=ArchitectureModelBuilder().build(modules,graph); health_score=ArchitectureHealthEngine().calculate(graph, findings, cycles); module_risks=ModuleRiskEngine().calculate(graph, findings); architecture_pattern=ArchitecturePatternDetector().detect(modules, graph)
        recommendations=AIRecommendationEngine().generate(findings,graph); redesign=ArchitectureRedesignEngine().propose(architecture,graph,findings); modernization=ModernizationPlanner().plan(findings,redesign); executive_summary=ExecutiveSummaryGenerator().generate(files,len(modules),len(edges),cycles,findings,recommendations,redesign)
        return AnalysisResult(analysis_id=uuid.uuid4().hex, project_name=project_name or Path(root).name, root=root, files=files, modules=modules, dependencies=edges, external_imports=external, unresolved_imports=unresolved, cycles=cycles, findings=findings, architecture=architecture, recommendations=recommendations, redesign=redesign, modernization=modernization, health_score=health_score, executive_summary=executive_summary, module_risks=module_risks, architecture_pattern=architecture_pattern, coverage=(len(modules)/len(files) if files else 0))
