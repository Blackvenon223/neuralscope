"""Impact analysis domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AffectedNode:
    node_id: str
    name: str
    file_path: str
    distance: int
    risk: RiskLevel


@dataclass
class ImpactReport:
    changed_files: list[str]
    affected: list[AffectedNode] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    summary: str = ""

    @property
    def affected_count(self) -> int:
        return len(self.affected)
