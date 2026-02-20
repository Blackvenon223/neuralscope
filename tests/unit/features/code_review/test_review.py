"""Tests for code review entities and LLM response parsing."""

import json

from neuralscope.features.code_review.domain.entities.review import (
    Issue,
    IssueCategory,
    ReviewResult,
    Severity,
)
from neuralscope.features.code_review.data.datasource.llm_reviewer.implementation import (
    LlmReviewerDatasource,
)


def test_review_result_properties():
    review = ReviewResult(
        file_path="app.py",
        score=8.5,
        summary="Clean code",
        issues=[
            Issue(line=10, message="unused import", severity=Severity.WARNING, category=IssueCategory.STYLE),
            Issue(line=25, message="SQL injection", severity=Severity.CRITICAL, category=IssueCategory.SECURITY),
        ],
        strengths=["Good naming"],
    )
    assert review.issue_count == 2
    assert review.critical_count == 1
    assert not review.passed


def test_review_result_passed():
    review = ReviewResult(file_path="ok.py", score=9.0, summary="Excellent")
    assert review.passed
    assert review.issue_count == 0


def test_parse_valid_json():
    raw = json.dumps({
        "score": 7.5,
        "summary": "Decent code",
        "issues": [
            {
                "line": 5,
                "message": "Missing docstring",
                "severity": "info",
                "category": "documentation",
                "suggestion": "Add a docstring",
            }
        ],
        "strengths": ["Clear logic"],
    })

    ds = LlmReviewerDatasource.__new__(LlmReviewerDatasource)
    result = ds._parse("test.py", raw)
    assert result.score == 7.5
    assert result.issue_count == 1
    assert result.issues[0].severity == Severity.INFO
    assert result.strengths == ["Clear logic"]


def test_parse_json_in_markdown_fences():
    raw = '```json\n{"score": 6.0, "summary": "OK", "issues": [], "strengths": []}\n```'
    ds = LlmReviewerDatasource.__new__(LlmReviewerDatasource)
    result = ds._parse("test.py", raw)
    assert result.score == 6.0


def test_parse_malformed_response():
    ds = LlmReviewerDatasource.__new__(LlmReviewerDatasource)
    result = ds._parse("test.py", "This is not JSON at all")
    assert result.score == 5.0
    assert "not JSON" in result.summary


def test_extract_json_strips_fences():
    text = '```json\n{"key": "value"}\n```'
    assert LlmReviewerDatasource._extract_json(text) == '{"key": "value"}'


def test_extract_json_finds_braces():
    text = 'Some preamble {"score": 10} trailing'
    assert LlmReviewerDatasource._extract_json(text) == '{"score": 10}'
