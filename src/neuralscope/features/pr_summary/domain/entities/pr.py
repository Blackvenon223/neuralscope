"""PR summary domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FileChange:
    file_path: str
    additions: int = 0
    deletions: int = 0
    change_type: str = "modified"


@dataclass
class PRSummary:
    diff_ref: str
    title: str = ""
    description: str = ""
    changes: list[FileChange] = field(default_factory=list)
    breaking_changes: list[str] = field(default_factory=list)
    rendered: str = ""

    @property
    def total_changes(self) -> int:
        return len(self.changes)
