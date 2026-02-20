"""Tests for test generator entities."""

import json

from neuralscope.features.test_generator.data.datasource.llm_test_writer.implementation import (
    LlmTestWriterDatasource,
)
from neuralscope.features.test_generator.domain.entities.test_suite import TestCase, TestSuite


def test_suite_count():
    suite = TestSuite(
        source_file="app.py",
        test_cases=[
            TestCase(name="test_a", body="assert True"),
            TestCase(name="test_b", body="assert 1 == 1"),
        ],
    )
    assert suite.count == 2


def test_parse_test_response():
    raw = json.dumps({
        "test_cases": [
            {"name": "test_add", "body": "assert add(1, 2) == 3", "description": "Tests addition"},
            {"name": "test_edge", "body": "assert add(0, 0) == 0", "description": "Zero case"},
        ]
    })
    ds = LlmTestWriterDatasource.__new__(LlmTestWriterDatasource)
    suite = ds._parse("math.py", raw)
    assert suite.count == 2
    assert suite.test_cases[0].name == "test_add"
    assert "Auto-generated" in suite.rendered
