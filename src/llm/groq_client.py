"""Thin Groq client wrapper."""

from __future__ import annotations

from groq import Groq

from src.config import Settings


class GroqLLM:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = Groq(api_key=settings.groq_api_key)

    def complete(self, system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.groq_model,
            temperature=self.settings.groq_temperature if temperature is None else temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
