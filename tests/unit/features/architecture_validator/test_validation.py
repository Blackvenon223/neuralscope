"""Tests for architecture validator entities."""

from neuralscope.features.architecture_validator.domain.entities.validation import (
    ValidationReport,
    Violation,
    ViolationSeverity,
)


def test_validation_report_passed():
    report = ValidationReport(
        project_path="/p",
        rules_checked=5,
        violations=[
            Violation(rule="naming", file_path="a.py", message="bad name", severity=ViolationSeverity.WARNING),
        ],
    )
    assert report.passed
    assert report.violation_count == 1


def test_validation_report_failed():
    report = ValidationReport(
        project_path="/p",
        violations=[
            Violation(rule="imports", file_path="b.py", message="circular", severity=ViolationSeverity.ERROR),
        ],
    )
    assert not report.passed
