"""Ask question use case."""

from __future__ import annotations

from dataclasses import dataclass

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.codebase_qa.domain.entities.answer import Answer
from neuralscope.features.codebase_qa.domain.repository.qa import IQARepository


@dataclass(frozen=True)
class AskQuestionParams:
    question: str
    project: str = "."


@dataclass(frozen=True)
class AskQuestionSuccess:
    answer: Answer

    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class AskQuestionError:
    message: str

    def is_success(self) -> bool:
        return False


class AskQuestionUseCase:
    def __init__(
        self,
        qa_repo: IQARepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._qa = qa_repo
        self._log_context = log_context_repository

    async def __call__(self, params: AskQuestionParams) -> AskQuestionSuccess | AskQuestionError:
        self._log_context.emit_input(question=params.question, project=params.project)

        if not params.question.strip():
            self._log_context.emit_result(result="error", reason="empty_question")
            return AskQuestionError("Question cannot be empty")

        try:
            answer = await self._qa.ask(params.question, params.project)
        except Exception as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return AskQuestionError(f"Q&A failed: {exc}")

        self._log_context.emit_result(
            result="success",
            sources=answer.source_count,
            confidence=answer.confidence,
        )
        return AskQuestionSuccess(answer=answer)
