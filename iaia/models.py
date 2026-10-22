from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

Severity = Literal['low', 'medium', 'high', 'critical']

class Finding(BaseModel):
    title: str
    category: str
    severity: Severity
    file_path: str
    line: int | None = None
    evidence: str
    explanation: str
    confidence: float = Field(ge=0, le=1)
    limitations: str
    recommendation: str = ''

class ArchitecturePattern(BaseModel):
    pattern: str
    confidence: float = Field(ge=0, le=1)
    explanation: str
    evidence: list[str] = []

class ModuleInfo(BaseModel):
    name: str
    path: str
    classes: list[str] = []
    functions: list[str] = []
    imports: list[str] = []
    lines: int = 0
    complexity: int = 0

class Recommendation(BaseModel):
    finding_title: str
    discovered: str
    evidence: str
    why_it_matters: str
    impact: str
    corrective_action: str
    preventive_measures: list[str]
    validation_tests: list[str]
    longer_term: str
    priority: str
    rationale: str
    confidence: float
    assumptions: list[str]
    limitations: str
    source: str = 'rule-based'

class RedesignProposal(BaseModel):
    title: str
    rationale: str
    benefits: list[str]
    tradeoffs: list[str]
    migration_risks: list[str]
    suggested_changes: list[str]

class ModernizationAction(BaseModel):
    phase: str
    title: str
    priority: str
    evidence: str
    reason: str
    steps: list[str]
    dependencies: list[str]
    validation: list[str]
    rollback: str
    benefits: list[str]
    uncertainty: str

class ArchitectureHealthScore(BaseModel):
    maintainability: float = Field(ge=0, le=100)
    security: float = Field(ge=0, le=100)
    coupling: float = Field(ge=0, le=100)
    complexity: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)
    dependency_count: int = 0
    module_count: int = 0
    circular_dependency_count: int = 0
    blast_radius_size: int = 0
    methodology: str = 'Deterministic heuristic; higher scores indicate better health.'

class ExecutiveSummary(BaseModel):
    project_size: str
    architecture_type: str
    top_risks: list[str] = []
    critical_findings: list[str] = []
    recommended_improvements: list[str] = []
    modernization_priority: str
    business_summary: str
    technical_summary: str

class ModuleRisk(BaseModel):
    module: str
    score: float = Field(ge=0, le=100)
    status: str
    finding_penalty: int
    blast_radius_size: int
    dependency_count: int
    explanation: str

class AnalysisResult(BaseModel):
    analysis_id: str
    project_name: str
    root: str
    files: list[str] = []
    modules: list[ModuleInfo] = []
    dependencies: list[tuple[str, str]] = []
    external_imports: dict[str, list[str]] = {}
    unresolved_imports: list[str] = []
    cycles: list[list[str]] = []
    findings: list[Finding] = []
    architecture: dict[str, Any] = {}
    blast_radius: dict[str, Any] = {}
    recommendations: list[Recommendation] = []
    redesign: list[RedesignProposal] = []
    modernization: list[ModernizationAction] = []
    health_score: ArchitectureHealthScore | None = None
    executive_summary: ExecutiveSummary | None = None
    module_risks: dict[str, ModuleRisk] = {}
    architecture_pattern: ArchitecturePattern | None = None
    errors: list[str] = []
    coverage: float = 0.0
    limitations: list[str] = ['Static indicators require engineering validation; graph impact is potential, not confirmed operational impact.']
