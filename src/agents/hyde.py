"""HyDE agent."""

from __future__ import annotations

from src.llm.openrouter_client import OpenRouterLLM


class HyDEAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def generate(self, question: str) -> str:
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
        return self.llm.complete(system_prompt, user_prompt, temperature=0.2).strip()