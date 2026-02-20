"""Comprehensive SDK wiring test — verifies all imports resolve."""


def test_sdk_import():
    from neuralscope.sdk.client import NeuralScope
    ns = NeuralScope()
    assert ns.model
    assert ns.profile == "default"


def test_sdk_list_models():
    from neuralscope.sdk.client import NeuralScope
    ns = NeuralScope()
    providers = ns.list_models()
    assert isinstance(providers, list)
    assert len(providers) >= 5


def test_all_feature_imports():
    from neuralscope.features.code_review.data.datasource.llm_reviewer.implementation import LlmReviewerDatasource
    from neuralscope.features.code_review.data.repository.reviewer import ReviewerRepository
    from neuralscope.features.documentation.data.datasource.llm_documenter.implementation import LlmDocumenterDatasource
    from neuralscope.features.documentation.data.repository.documenter import DocumenterRepository
    from neuralscope.features.vulnerability_scan.data.datasource.llm_scanner.implementation import LlmSecurityScanner
    from neuralscope.features.vulnerability_scan.data.repository.scanner import ScannerRepository
    from neuralscope.features.test_generator.data.datasource.llm_test_writer.implementation import LlmTestWriterDatasource
    from neuralscope.features.test_generator.data.repository.generator import GeneratorRepository
    from neuralscope.features.codebase_qa.data.datasource.file_indexer.implementation import FileIndexer
    from neuralscope.features.codebase_qa.data.datasource.llm_answerer.implementation import LlmAnswerer
    from neuralscope.features.codebase_qa.data.repository.qa import QARepository
    from neuralscope.features.health_dashboard.data.repository.health import HealthRepository
    from neuralscope.features.prompt_studio.data.datasource.prompt_storage.implementation import FileProfileRepository
    from neuralscope.features.dependency_graph.data.datasource.ast_parser.implementation import AstParser
    from neuralscope.features.dependency_graph.data.datasource.graph_renderer.implementation import GraphRenderer
    from neuralscope.features.dependency_graph.data.repository.graph_builder import GraphBuilderRepository
    from neuralscope.features.dependency_graph.data.repository.impact_analyzer import ImpactAnalyzerRepository
    assert True


def test_cli_import():
    from neuralscope.cli.app import app
    assert app is not None
