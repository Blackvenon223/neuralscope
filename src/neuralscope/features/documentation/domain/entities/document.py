"""Documentation domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DocFormat(str, Enum):
    MARKDOWN = "markdown"
    RST = "rst"
    HTML = "html"


@dataclass(frozen=True)
class FunctionDoc:
    name: str
    signature: str
    docstring: str
    params: list[str] = field(default_factory=list)
    returns: str = ""


@dataclass(frozen=True)
class ClassDoc:
    name: str
    docstring: str
    methods: list[FunctionDoc] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)


@dataclass
class GeneratedDoc:
    file_path: str
    module_docstring: str
    classes: list[ClassDoc] = field(default_factory=list)
    functions: list[FunctionDoc] = field(default_factory=list)
    rendered: str = ""

    @property
    def item_count(self) -> int:
        return len(self.classes) + len(self.functions)
