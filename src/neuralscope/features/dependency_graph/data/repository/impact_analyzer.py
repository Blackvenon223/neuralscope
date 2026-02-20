"""Data layer implementation of impact analyzer."""

from __future__ import annotations

from neuralscope.features.dependency_graph.domain.entities.graph import DependencyGraph
from neuralscope.features.dependency_graph.domain.entities.impact import (
    AffectedNode,
    ImpactReport,
    RiskLevel,
)
from neuralscope.features.dependency_graph.domain.repository.impact_analyzer import (
    IImpactAnalyzerRepository,
)


class ImpactAnalyzerRepository(IImpactAnalyzerRepository):
    async def analyze(self, graph: DependencyGraph, changed_files: list[str]) -> ImpactReport:
        changed_modules = self._files_to_module_ids(graph, changed_files)
        affected = self._find_affected(graph, changed_modules)
        risk = self._assess_risk(affected)
        return ImpactReport(
            changed_files=changed_files,
            affected=affected,
            risk_level=risk,
        )

    def _files_to_module_ids(self, graph: DependencyGraph, files: list[str]) -> set[str]:
        lookup = {n.file_path: n.id for n in graph.nodes}
        result = set()
        for f in files:
            normalized = f.replace("\\", "/")
            for file_path, node_id in lookup.items():
                if normalized.endswith(file_path) or file_path.endswith(normalized):
                    result.add(node_id)
        return result

    def _find_affected(
        self,
        graph: DependencyGraph,
        changed_modules: set[str],
    ) -> list[AffectedNode]:
        affected: list[AffectedNode] = []
        visited: set[str] = set()

        def walk(node_id: str, distance: int) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            dependents = graph.get_dependents(node_id)
            for dep_id in dependents:
                if dep_id in changed_modules or dep_id in visited:
                    continue
                node = graph.get_node(dep_id)
                if node:
                    affected.append(
                        AffectedNode(
                            node_id=dep_id,
                            name=node.name,
                            file_path=node.file_path,
                            distance=distance,
                            risk=RiskLevel.HIGH if distance <= 1 else RiskLevel.MEDIUM,
                        )
                    )
                walk(dep_id, distance + 1)

        for module_id in changed_modules:
            walk(module_id, 1)

        return affected

    @staticmethod
    def _assess_risk(affected: list[AffectedNode]) -> RiskLevel:
        if not affected:
            return RiskLevel.LOW
        if len(affected) > 10:
            return RiskLevel.CRITICAL
        if any(a.distance <= 1 for a in affected):
            return RiskLevel.HIGH
        return RiskLevel.MEDIUM
