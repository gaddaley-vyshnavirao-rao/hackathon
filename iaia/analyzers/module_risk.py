from __future__ import annotations

import networkx as nx
from iaia.models import Finding, ModuleRisk


class ModuleRiskEngine:
    """Calculate deterministic, reviewable risk indicators for each module."""

    def calculate(self, graph: nx.DiGraph, findings: list[Finding]) -> dict[str, ModuleRisk]:
        by_file: dict[str, list[Finding]] = {}
        for finding in findings:
            by_file.setdefault(finding.file_path.replace('\\', '/'), []).append(finding)

        result = {}
        for module in graph.nodes:
            module_path = module.replace('.', '/') + '.py'
            module_findings = by_file.get(module_path, [])
            finding_penalty = sum({'critical': 40, 'high': 25, 'medium': 12, 'low': 4}.get(f.severity, 0) for f in module_findings)
            blast_radius_size = len(nx.ancestors(graph, module)) + len(nx.descendants(graph, module))
            dependency_count = graph.in_degree(module) + graph.out_degree(module)
            score = min(100, finding_penalty + blast_radius_size * 10 + dependency_count * 5)
            status = 'red' if score >= 50 else 'yellow' if score > 25 else 'green'
            result[module] = ModuleRisk(
                module=module,
                score=round(float(score), 1),
                status=status,
                finding_penalty=finding_penalty,
                blast_radius_size=blast_radius_size,
                dependency_count=dependency_count,
                explanation='Score combines finding severity, graph blast radius, and total direct dependency degree; it is a static risk indicator.',
            )
        return result
