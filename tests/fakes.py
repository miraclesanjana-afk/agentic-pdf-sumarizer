"""Offline fake chat models for agent tests."""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field


class FakeToolModel(BaseChatModel):
    """Returns preprogrammed messages and pretends tool binding succeeded."""

    responses: list[BaseMessage] = Field(default_factory=list)
    i: int = 0

    @property
    def _llm_type(self) -> str:
        return "fake-tool-calling"

    def bind_tools(self, tools: Any, **kwargs: Any) -> FakeToolModel:
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        message = self.responses[self.i % len(self.responses)]
        self.i += 1
        return ChatResult(generations=[ChatGeneration(message=message)])
