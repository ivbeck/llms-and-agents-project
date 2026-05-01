"""OpenRouter client using LangChain."""

from __future__ import annotations

from typing import Any

from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from src.config import Settings


class OpenRouterLLM:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = ChatOpenRouter(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            temperature=settings.openrouter_temperature,
            base_url=settings.openrouter_base_url,
        )

    def _messages_to_dicts(self, system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def complete(self, system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
        messages = self._messages_to_dicts(system_prompt, user_prompt)
        if temperature is not None:
            result = self.model.bind(temperature=temperature).invoke(messages)
        else:
            result = self.model.invoke(messages)
        if isinstance(result, list):
            return result[0].content if result else ""
        return result.content

    def bind(self, **kwargs: Any) -> "OpenRouterLLM":
        self.model = self.model.bind(**kwargs)
        return self