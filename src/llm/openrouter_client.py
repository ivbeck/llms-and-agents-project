"""OpenRouter client using LangChain."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

from langchain_openrouter import ChatOpenRouter

from src.config import Settings
from src.models import LLMCallUsage

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
        self.usage_callback: Callable[[LLMCallUsage], None] | None = None
        logger.info("OpenRouterLLM initialized with model=%s, temperature=%.1f", settings.openrouter_model, settings.openrouter_temperature)

    def _messages_to_dicts(self, system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def _first_int(self, data: dict[str, Any], keys: tuple[str, ...]) -> int:
        for key in keys:
            value = data.get(key)
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                return int(value)
        return 0

    def _usage_from_result(self, result: Any, prompt_chars: int, completion_chars: int) -> LLMCallUsage:
        usage_candidates: list[dict[str, Any]] = []
        usage_metadata = getattr(result, "usage_metadata", None)
        if isinstance(usage_metadata, dict):
            usage_candidates.append(usage_metadata)

        response_metadata = getattr(result, "response_metadata", None)
        if isinstance(response_metadata, dict):
            for key in ("token_usage", "usage"):
                value = response_metadata.get(key)
                if isinstance(value, dict):
                    usage_candidates.append(value)

        additional_kwargs = getattr(result, "additional_kwargs", None)
        if isinstance(additional_kwargs, dict):
            for key in ("usage", "token_usage"):
                value = additional_kwargs.get(key)
                if isinstance(value, dict):
                    usage_candidates.append(value)

        merged: dict[str, Any] = {}
        for candidate in usage_candidates:
            merged.update(candidate)

        prompt_tokens = self._first_int(merged, ("prompt_tokens", "input_tokens"))
        completion_tokens = self._first_int(merged, ("completion_tokens", "output_tokens"))
        total_tokens = self._first_int(merged, ("total_tokens",))
        reasoning_tokens = self._first_int(merged, ("reasoning_tokens",))

        output_token_details = merged.get("output_token_details")
        if isinstance(output_token_details, dict):
            reasoning_tokens = reasoning_tokens or self._first_int(output_token_details, ("reasoning", "reasoning_tokens"))
        completion_tokens_details = merged.get("completion_tokens_details")
        if isinstance(completion_tokens_details, dict):
            reasoning_tokens = reasoning_tokens or self._first_int(completion_tokens_details, ("reasoning_tokens",))

        if total_tokens == 0 and (prompt_tokens or completion_tokens or reasoning_tokens):
            total_tokens = prompt_tokens + completion_tokens + reasoning_tokens

        return LLMCallUsage(
            model=self.settings.openrouter_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            reasoning_tokens=reasoning_tokens,
            usage_available=bool(usage_candidates),
            prompt_chars=prompt_chars,
            completion_chars=completion_chars,
        )

    def complete(self, system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
        messages = self._messages_to_dicts(system_prompt, user_prompt)
        prompt_chars = sum(len(message["content"]) for message in messages)
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                if temperature is not None:
                    result = self.model.bind(temperature=temperature).invoke(messages)
                else:
                    result = self.model.invoke(messages)
                content = result.content if not isinstance(result, list) else (result[0].content if result else "")
                content_text = str(content)
                usage_source = result[0] if isinstance(result, list) and result else result
                usage = self._usage_from_result(usage_source, prompt_chars, len(content_text))
                if self.usage_callback is not None:
                    self.usage_callback(usage)
                logger.debug("LLM response length=%d, model=%s", len(content_text), self.settings.openrouter_model)
                return content_text
            except Exception as exc:
                last_error = exc
                logger.warning("LLM call failed on attempt %d/3: %s", attempt, exc)
                if attempt < 3:
                    time.sleep(0.75 * attempt)

        raise RuntimeError(f"LLM call failed after retries: {last_error}") from last_error
