"""NeuralScope SDK client.

Usage:
    from neuralscope import NeuralScope

    ns = NeuralScope(model="openai/gpt-5.2")
    review = await ns.review("./src/auth/service.py")
    answer = await ns.ask("How does auth work?", project="./src")
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from langchain_core.language_models import BaseChatModel

from neuralscope.core.llm.model_registry import ModelRegistry
from neuralscope.core.llm.models import ModelConfig
from neuralscope.core.log_context import LogContextRepository
from neuralscope.core.settings import Settings, get_settings


class NeuralScope:
    """Main SDK entry point. CLI and MCP are thin wrappers over this class."""

    def __init__(
        self,
        model: Optional[str] = None,
        profile: str = "default",
        settings: Optional[Settings] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._model_string = model or self._settings.get_model_string()
        self._profile = profile
        self._registry = ModelRegistry(self._settings)
        self._llm: Optional[BaseChatModel] = None

    @property
    def model(self) -> str:
        return self._model_string

    @property
    def profile(self) -> str:
        return self._profile

    def _get_llm(self) -> BaseChatModel:
        if self._llm is None:
            config = ModelConfig.from_string(self._model_string)
            self._llm = self._registry.get(config)
        return self._llm

    def _log(self, name: str) -> LogContextRepository:
        return LogContextRepository(name)

    # ── Code Review ────────────────────────────────────────────────────────

    async def review(self, path: str, *, diff: bool = False) -> dict:
        from neuralscope.features.code_review.data.datasource.llm_reviewer.implementation import (
            LlmReviewerDatasource,
        )
        from neuralscope.features.code_review.data.repository.reviewer import ReviewerRepository
        from neuralscope.features.code_review.domain.use_cases.review_file.use_case import (
            ReviewFileParams,
            ReviewFileUseCase,
        )

        ds = LlmReviewerDatasource(self._get_llm())
        repo = ReviewerRepository(ds)
        uc = ReviewFileUseCase(reviewer_repo=repo, log_context_repository=self._log("review"))
        result = await uc(ReviewFileParams(path=path, diff=diff))
        if result.is_success():
            r = result.review
            return {
                "file": r.file_path, "score": r.score, "summary": r.summary,
                "issues": [{"line": i.line, "message": i.message, "severity": i.severity.value, "category": i.category.value, "suggestion": i.suggestion} for i in r.issues],
                "strengths": r.strengths, "passed": r.passed,
            }
        return {"error": result.message}

    # ── Documentation ──────────────────────────────────────────────────────

    async def docs(self, path: str, *, format: str = "markdown") -> dict:
        from neuralscope.features.documentation.data.datasource.llm_documenter.implementation import (
            LlmDocumenterDatasource,
        )
        from neuralscope.features.documentation.data.repository.documenter import DocumenterRepository
        from neuralscope.features.documentation.domain.use_cases.generate_file_docs.use_case import (
            GenerateFileDocsParams,
            GenerateFileDocsUseCase,
        )

        ds = LlmDocumenterDatasource(self._get_llm())
        repo = DocumenterRepository(ds)
        uc = GenerateFileDocsUseCase(documenter_repo=repo, log_context_repository=self._log("docs"))
        result = await uc(GenerateFileDocsParams(path=path, format=format))
        if result.is_success():
            d = result.doc
            return {"file": d.file_path, "module_docstring": d.module_docstring, "items": d.item_count, "rendered": d.rendered}
        return {"error": result.message}

    # ── Dependency Graph ───────────────────────────────────────────────────

    async def build_graph(self, path: str, *, output: str = "svg", mode: str = "ast") -> dict:
        from neuralscope.features.dependency_graph.data.repository.graph_builder import GraphBuilderRepository
        from neuralscope.features.dependency_graph.domain.use_cases.build_graph.use_case import (
            BuildGraphParams,
            BuildGraphUseCase,
        )

        llm = self._get_llm() if mode == "llm" else None
        repo = GraphBuilderRepository(llm=llm)
        uc = BuildGraphUseCase(graph_builder_repo=repo, log_context_repository=self._log("graph"))
        result = await uc(BuildGraphParams(path=path, output_format=output, mode=mode))
        if result.is_success():
            return {"nodes": result.graph.node_count, "edges": result.graph.edge_count, "rendered": result.rendered, "mode": mode}
        return {"error": result.message}

    async def impact(self, path: str, *, diff: str = "HEAD~1") -> dict:
        from neuralscope.features.dependency_graph.data.repository.graph_builder import GraphBuilderRepository
        from neuralscope.features.dependency_graph.data.repository.impact_analyzer import ImpactAnalyzerRepository
        from neuralscope.features.dependency_graph.domain.use_cases.analyze_impact.use_case import (
            AnalyzeImpactParams,
            AnalyzeImpactUseCase,
        )

        builder = GraphBuilderRepository()
        analyzer = ImpactAnalyzerRepository()
        uc = AnalyzeImpactUseCase(
            graph_builder_repo=builder, impact_repo=analyzer, log_context_repository=self._log("impact")
        )
        result = await uc(AnalyzeImpactParams(path=path, changed_files=[diff]))
        if result.is_success():
            r = result.report
            return {"risk": r.overall_risk.value, "affected": len(r.affected_nodes), "summary": r.summary}
        return {"error": result.message}

    # ── Vulnerability Scan ─────────────────────────────────────────────────

    async def scan(self, path: str) -> dict:
        from neuralscope.features.vulnerability_scan.data.datasource.llm_scanner.implementation import (
            LlmSecurityScanner,
        )
        from neuralscope.features.vulnerability_scan.data.repository.scanner import ScannerRepository
        from neuralscope.features.vulnerability_scan.domain.use_cases.scan_project.use_case import (
            ScanProjectParams,
            ScanProjectUseCase,
        )

        scanner = LlmSecurityScanner(self._get_llm())
        repo = ScannerRepository(scanner)
        uc = ScanProjectUseCase(scanner_repo=repo, log_context_repository=self._log("scan"))
        result = await uc(ScanProjectParams(path=path))
        if result.is_success():
            r = result.report
            return {
                "total": r.total, "critical": r.critical_count, "high": r.high_count,
                "passed": r.passed, "summary": r.summary,
                "vulnerabilities": [{"id": v.id, "title": v.title, "severity": v.severity.value, "file": v.file_path, "line": v.line, "description": v.description, "recommendation": v.recommendation} for v in r.vulnerabilities],
            }
        return {"error": result.message}

    # ── Test Generator ─────────────────────────────────────────────────────

    async def generate_tests(self, path: str) -> dict:
        from neuralscope.features.test_generator.data.datasource.llm_test_writer.implementation import (
            LlmTestWriterDatasource,
        )
        from neuralscope.features.test_generator.data.repository.generator import GeneratorRepository
        from neuralscope.features.test_generator.domain.use_cases.generate_tests.use_case import (
            GenerateTestsParams,
            GenerateTestsUseCase,
        )

        ds = LlmTestWriterDatasource(self._get_llm())
        repo = GeneratorRepository(ds)
        uc = GenerateTestsUseCase(generator_repo=repo, log_context_repository=self._log("test_gen"))
        result = await uc(GenerateTestsParams(path=path))
        if result.is_success():
            s = result.suite
            return {"source_file": s.source_file, "tests": s.count, "rendered": s.rendered}
        return {"error": result.message}

    # ── Codebase Q&A ───────────────────────────────────────────────────────

    async def ask(self, question: str, *, project: str = ".") -> dict:
        from neuralscope.features.codebase_qa.data.datasource.file_indexer.implementation import FileIndexer
        from neuralscope.features.codebase_qa.data.datasource.llm_answerer.implementation import LlmAnswerer
        from neuralscope.features.codebase_qa.data.repository.qa import QARepository
        from neuralscope.features.codebase_qa.domain.use_cases.ask_question.use_case import (
            AskQuestionParams,
            AskQuestionUseCase,
        )

        indexer = FileIndexer()
        answerer = LlmAnswerer(self._get_llm())
        repo = QARepository(indexer, answerer)
        uc = AskQuestionUseCase(qa_repo=repo, log_context_repository=self._log("ask"))
        result = await uc(AskQuestionParams(question=question, project=project))
        if result.is_success():
            a = result.answer
            return {
                "answer": a.answer, "confidence": a.confidence,
                "sources": [{"file": s.file_path, "lines": f"{s.line_start}-{s.line_end}", "snippet": s.snippet} for s in a.sources],
            }
        return {"error": result.message}

    # ── Health Dashboard ───────────────────────────────────────────────────

    async def health(self, path: str) -> dict:
        from neuralscope.features.health_dashboard.data.repository.health import HealthRepository
        from neuralscope.features.health_dashboard.domain.use_cases.analyze_health.use_case import (
            AnalyzeHealthParams,
            AnalyzeHealthUseCase,
        )

        repo = HealthRepository()
        uc = AnalyzeHealthUseCase(health_repo=repo, log_context_repository=self._log("health"))
        result = await uc(AnalyzeHealthParams(path=path))
        if result.is_success():
            r = result.report
            return {
                "files": r.total_files, "lines": r.total_lines,
                "avg_complexity": r.avg_complexity, "health_score": r.health_score,
                "hotspots": [{"file": h.file_path, "complexity": h.complexity, "rank": h.rank} for h in r.hotspots],
            }
        return {"error": result.message}

    # ── PR Summary ─────────────────────────────────────────────────────────

    async def pr_summary(self, *, diff: str = "HEAD~1") -> dict:
        from neuralscope.features.code_review.data.datasource.llm_reviewer.implementation import (
            LlmReviewerDatasource,
        )
        from neuralscope.features.code_review.data.repository.reviewer import ReviewerRepository
        from neuralscope.features.code_review.domain.use_cases.review_diff.use_case import (
            ReviewDiffParams,
            ReviewDiffUseCase,
        )

        ds = LlmReviewerDatasource(self._get_llm())
        repo = ReviewerRepository(ds)
        uc = ReviewDiffUseCase(reviewer_repo=repo, log_context_repository=self._log("pr_summary"))
        result = await uc(ReviewDiffParams(diff_ref=diff))
        if result.is_success():
            r = result.review
            return {"score": r.score, "summary": r.summary, "issues": r.issue_count}
        return {"error": result.message}

    # ── Architecture Validator ─────────────────────────────────────────────

    async def validate_arch(self, path: str, *, rules: Optional[str] = None) -> dict:
        from neuralscope.features.health_dashboard.data.repository.health import HealthRepository
        from neuralscope.features.health_dashboard.domain.use_cases.analyze_health.use_case import (
            AnalyzeHealthParams,
            AnalyzeHealthUseCase,
        )

        repo = HealthRepository()
        uc = AnalyzeHealthUseCase(health_repo=repo, log_context_repository=self._log("validate"))
        result = await uc(AnalyzeHealthParams(path=path))
        if result.is_success():
            r = result.report
            hotspot_violations = [{"file": h.file_path, "complexity": h.complexity} for h in r.hotspots if h.complexity > 10]
            return {"passed": len(hotspot_violations) == 0, "violations": hotspot_violations, "health_score": r.health_score}
        return {"error": result.message}

    # ── Prompt Management ──────────────────────────────────────────────────

    async def create_profile(self, name: str, *, config: Optional[dict] = None) -> dict:
        from neuralscope.features.prompt_studio.data.datasource.prompt_storage.implementation import (
            FileProfileRepository,
        )
        from neuralscope.features.prompt_studio.domain.use_cases.create_profile.use_case import (
            CreateProfileParams,
            CreateProfileUseCase,
        )

        profiles_dir = Path.home() / ".neuralscope" / "profiles"
        repo = FileProfileRepository(profiles_dir)
        uc = CreateProfileUseCase(profile_repo=repo, log_context_repository=self._log("profile"))
        cfg = config or {}
        result = await uc(CreateProfileParams(
            name=name,
            description=cfg.get("description", ""),
            system_prompt=cfg.get("system_prompt", ""),
            temperature=cfg.get("temperature", 0.7),
        ))
        if result.is_success():
            return result.profile.to_dict()
        return {"error": result.message}

    async def improve_prompt(self, *, profile: str, task: str) -> str:
        return f"[{profile}] Optimized prompt for: {task}"

    async def list_profiles(self) -> list[dict]:
        from neuralscope.features.prompt_studio.data.datasource.prompt_storage.implementation import (
            FileProfileRepository,
        )

        profiles_dir = Path.home() / ".neuralscope" / "profiles"
        repo = FileProfileRepository(profiles_dir)
        profiles = await repo.list_all()
        return [p.to_dict() for p in profiles]

    # ── Model Info ─────────────────────────────────────────────────────────

    def list_models(self) -> list[dict[str, str]]:
        return self._registry.list_providers()
