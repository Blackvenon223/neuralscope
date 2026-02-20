"""Prompt profile domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PromptProfile:
    name: str
    description: str = ""
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> PromptProfile:
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            system_prompt=data.get("system_prompt", ""),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 4096),
            tags=data.get("tags", []),
        )
