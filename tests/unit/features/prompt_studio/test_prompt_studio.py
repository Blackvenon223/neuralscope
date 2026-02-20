"""Tests for prompt studio feature."""

from pathlib import Path

import pytest

from neuralscope.features.prompt_studio.domain.entities.prompt_profile import PromptProfile
from neuralscope.features.prompt_studio.data.datasource.prompt_storage.implementation import (
    FileProfileRepository,
)
from neuralscope.core.log_context import LogContextRepository
from neuralscope.features.prompt_studio.domain.use_cases.create_profile.use_case import (
    CreateProfileParams,
    CreateProfileUseCase,
)


def test_profile_serialization():
    profile = PromptProfile(name="reviewer", description="Code reviewer", temperature=0.3)
    data = profile.to_dict()
    restored = PromptProfile.from_dict(data)
    assert restored.name == "reviewer"
    assert restored.temperature == 0.3


@pytest.mark.asyncio
async def test_file_profile_crud(tmp_path: Path):
    repo = FileProfileRepository(tmp_path / "profiles")
    profile = PromptProfile(name="test", description="Test profile")

    await repo.save(profile)
    loaded = await repo.get("test")
    assert loaded is not None
    assert loaded.name == "test"

    all_profiles = await repo.list_all()
    assert len(all_profiles) == 1

    deleted = await repo.delete("test")
    assert deleted
    assert await repo.get("test") is None


@pytest.mark.asyncio
async def test_create_profile_success(tmp_path: Path):
    repo = FileProfileRepository(tmp_path / "profiles")
    uc = CreateProfileUseCase(
        profile_repo=repo,
        log_context_repository=LogContextRepository("create_profile"),
    )
    result = await uc(CreateProfileParams(name="myprofile", description="Test"))
    assert result.is_success()
    assert result.profile.name == "myprofile"


@pytest.mark.asyncio
async def test_create_profile_duplicate(tmp_path: Path):
    repo = FileProfileRepository(tmp_path / "profiles")
    await repo.save(PromptProfile(name="dup"))
    uc = CreateProfileUseCase(
        profile_repo=repo,
        log_context_repository=LogContextRepository("create_profile"),
    )
    result = await uc(CreateProfileParams(name="dup"))
    assert not result.is_success()
