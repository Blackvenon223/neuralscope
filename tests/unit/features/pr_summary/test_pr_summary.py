"""Tests for PR summary entities."""

from neuralscope.features.pr_summary.domain.entities.pr import FileChange, PRSummary


def test_pr_summary_total_changes():
    pr = PRSummary(
        diff_ref="HEAD~1",
        title="Fix auth bug",
        changes=[
            FileChange(file_path="auth.py", additions=10, deletions=5),
            FileChange(file_path="tests.py", additions=20),
        ],
    )
    assert pr.total_changes == 2


def test_pr_summary_empty():
    pr = PRSummary(diff_ref="HEAD~1")
    assert pr.total_changes == 0
