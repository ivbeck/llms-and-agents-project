"""OpenRouter client using LangChain."""

from __future__ import annotations

import logging
from typing import Any

from langchain_openrouter import ChatOpenRouter

from src.config import Settings

logger = logging.getLogger(__name__)


class OpenRouterLLM:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = ChatOpenRouter(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            temperature=settings.openrouter_temperature,
            base_url=settings.openrouter_base_url,
        )
        logger.info("OpenRouterLLM initialized with model=%s, temperature=%.1f", settings.openrouter_model, settings.openrouter_temperature)

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
        content = result.content if not isinstance(result, list) else (result[0].content if result else "")
        logger.debug("LLM response length=%d, model=%s", len(content), self.settings.openrouter_model)
        return content