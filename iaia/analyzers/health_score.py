from __future__ import annotations

import networkx as nx
from iaia.models import ArchitectureHealthScore, Finding


class ArchitectureHealthEngine:
    """Calculate explainable architecture health indicators without executing source."""

    @staticmethod
    def _score(value: float) -> float:
        return round(max(0.0, min(100.0, value)), 1)

    def calculate(self, graph: nx.DiGraph, findings: list[Finding], cycles: list[list[str]] | None = None) -> ArchitectureHealthScore:
        modules = graph.number_of_nodes()
        dependencies = graph.number_of_edges()
        circular_count = len(cycles or list(nx.simple_cycles(graph)))
        density = dependencies / max(modules, 1)
        severity_penalty = sum({'critical': 25, 'high': 15, 'medium': 7, 'low': 2}.get(f.severity, 0) for f in findings)

        reachable_sizes = []
        for node in graph:
            reachable_sizes.append(len(nx.descendants(graph, node)) + len(nx.ancestors(graph, node)))
        blast_radius_size = max(reachable_sizes, default=0)

        maintainability = self._score(100 - density * 18 - circular_count * 12 - len(findings) * 2)
        security = self._score(100 - severity_penalty)
        coupling = self._score(100 - density * 25 - circular_count * 15)
        complexity = self._score(100 - (blast_radius_size / max(modules, 1)) * 50 - density * 10 - circular_count * 10)
        overall = self._score((maintainability + security + coupling + complexity) / 4)

        return ArchitectureHealthScore(
            maintainability=maintainability,
            security=security,
            coupling=coupling,
            complexity=complexity,
            overall=overall,
            dependency_count=dependencies,
            module_count=modules,
            circular_dependency_count=circular_count,
            blast_radius_size=blast_radius_size,
        )
