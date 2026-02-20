"""Tests for health dashboard feature."""

from pathlib import Path

import pytest

from neuralscope.core.log_context import LogContextRepository
from neuralscope.features.health_dashboard.data.datasource.complexity_analyzer.implementation import (  # noqa: E501
    ComplexityAnalyzer,
)
from neuralscope.features.health_dashboard.data.repository.health import HealthRepository
from neuralscope.features.health_dashboard.domain.entities.health import (
    ComplexityMetric,
    HealthReport,
)
from neuralscope.features.health_dashboard.domain.use_cases.analyze_health.use_case import (
    AnalyzeHealthParams,
    AnalyzeHealthUseCase,
)


def test_health_score_good():
    report = HealthReport(project_path="/p", avg_complexity=3.0, test_coverage=80.0)
    assert report.health_score >= 9.0


def test_health_score_bad():
    report = HealthReport(
        project_path="/p",
        avg_complexity=15.0,
        test_coverage=30.0,
        hotspots=[
            ComplexityMetric(
                file_path=f"f{i}.py",
                function_name="x",
                complexity=20,
            )
            for i in range(6)
        ],
    )
    assert report.health_score <= 5.0


@pytest.mark.asyncio
async def test_complexity_analyzer(tmp_path: Path):
    (tmp_path / "app.py").write_text("def main():\n    if True:\n        pass\n")
    (tmp_path / "utils.py").write_text("x = 1\n")

    analyzer = ComplexityAnalyzer()
    report = await analyzer.analyze(str(tmp_path))
    assert report.total_files == 2
    assert report.total_lines > 0
    assert report.avg_complexity > 0


@pytest.mark.asyncio
async def test_analyze_health_use_case(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')\n")

    uc = AnalyzeHealthUseCase(
        health_repo=HealthRepository(),
        log_context_repository=LogContextRepository("analyze_health"),
    )
    result = await uc(AnalyzeHealthParams(path=str(tmp_path)))
    assert result.is_success()
    assert result.report.total_files == 1
