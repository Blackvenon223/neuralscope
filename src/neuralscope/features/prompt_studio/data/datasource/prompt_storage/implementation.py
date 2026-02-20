"""File-based prompt profile storage datasource."""

from __future__ import annotations

import json
from pathlib import Path

from neuralscope.features.prompt_studio.domain.entities.prompt_profile import PromptProfile
from neuralscope.features.prompt_studio.domain.repository.profile import IProfileRepository


class FileProfileRepository(IProfileRepository):
    """Stores profiles as JSON files in a directory."""

    def __init__(self, profiles_dir: Path) -> None:
        self._dir = profiles_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    async def save(self, profile: PromptProfile) -> None:
        path = self._dir / f"{profile.name}.json"
        path.write_text(json.dumps(profile.to_dict(), indent=2))

    async def get(self, name: str) -> PromptProfile | None:
        path = self._dir / f"{name}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return PromptProfile.from_dict(data)

    async def list_all(self) -> list[PromptProfile]:
        profiles = []
        for p in sorted(self._dir.glob("*.json")):
            data = json.loads(p.read_text())
            profiles.append(PromptProfile.from_dict(data))
        return profiles

    async def delete(self, name: str) -> bool:
        path = self._dir / f"{name}.json"
        if path.exists():
            path.unlink()
            return True
        return False
