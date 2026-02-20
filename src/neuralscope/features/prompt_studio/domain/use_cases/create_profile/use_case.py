"""Create/list profiles use case."""

from __future__ import annotations

from dataclasses import dataclass

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.prompt_studio.domain.entities.prompt_profile import PromptProfile
from neuralscope.features.prompt_studio.domain.repository.profile import IProfileRepository


@dataclass(frozen=True)
class CreateProfileParams:
    name: str
    description: str = ""
    system_prompt: str = ""
    temperature: float = 0.7


@dataclass(frozen=True)
class CreateProfileSuccess:
    profile: PromptProfile

    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class CreateProfileError:
    message: str

    def is_success(self) -> bool:
        return False


class CreateProfileUseCase:
    def __init__(
        self,
        profile_repo: IProfileRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._repo = profile_repo
        self._log_context = log_context_repository

    async def __call__(
        self,
        params: CreateProfileParams,
    ) -> CreateProfileSuccess | CreateProfileError:
        self._log_context.emit_input(name=params.name)

        existing = await self._repo.get(params.name)
        if existing:
            self._log_context.emit_result(result="error", reason="already_exists")
            return CreateProfileError(f"Profile '{params.name}' already exists")

        profile = PromptProfile(
            name=params.name,
            description=params.description,
            system_prompt=params.system_prompt,
            temperature=params.temperature,
        )
        await self._repo.save(profile)

        self._log_context.emit_result(result="success")
        return CreateProfileSuccess(profile=profile)
