"""Critic / self-reflection agent."""

from __future__ import annotations

from src.llm.openrouter_client import OpenRouterLLM
from src.models import ChunkEvidence, CriticResult
from src.utils.parsing import extract_json_object


class CriticAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def review(self, question: str, answer: str, evidence: list[ChunkEvidence]) -> CriticResult:
        evidence_block = []
        for idx, item in enumerate(evidence, start=1):
            evidence_block.append(f"[Evidence {idx}] {item.title} | {item.url}\n{item.text}\n")

        system_prompt = (
            "You are a critic agent for a RAG system. "
            "Evaluate groundedness and question relevance. Return only JSON."
        )
        user_prompt = f"""
Question:
{question}

Answer:
{answer}

Evidence:
{'\\n'.join(evidence_block)}

Return JSON only:
{{
  "is_grounded": true,
  "is_relevant": true,
  "needs_revision": false,
  "comment": "short explanation"
}}
"""
        try:
            raw = self.llm.complete(system_prompt, user_prompt)
            data = extract_json_object(raw)
            return CriticResult(
                is_grounded=bool(data.get("is_grounded", False)),
                is_relevant=bool(data.get("is_relevant", False)),
                needs_revision=bool(data.get("needs_revision", False)),
                comment=str(data.get("comment", "No critic comment.")).strip(),
            )
        except Exception:
            return CriticResult(
                is_grounded=False,
                is_relevant=True,
                needs_revision=False,
                comment="Critic output could not be parsed.",
            )