"""HyDE agent."""

from __future__ import annotations

import logging

from src.llm.openrouter_client import OpenRouterLLM

logger = logging.getLogger(__name__)


class HyDEAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def generate(self, question: str) -> str:
        logger.info("Generating HyDE document for question")
        system_prompt = (
            "You generate a short hypothetical answer document for retrieval purposes only. "
            "It should sound like a plausible source passage that could answer the question."
        )
        user_prompt = f"""
Write a compact hypothetical evidence passage for the question below.
Rules:
- 120 to 220 words
- informational style
- no bullet points
- do not mention that this is hypothetical

Question:
{question}
"""
        result = self.llm.complete(system_prompt, user_prompt, temperature=0.2).strip()
        logger.info("HyDE document generated, length=%d", len(result))
        return result