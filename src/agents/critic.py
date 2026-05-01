"""Critic / self-reflection agent."""

from __future__ import annotations

import logging

from src.llm.openrouter_client import OpenRouterLLM
from src.models import ChunkEvidence, CriticResult
from src.utils.parsing import extract_json_object

logger = logging.getLogger(__name__)


class CriticAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def review(self, question: str, answer: str, evidence: list[ChunkEvidence]) -> CriticResult:
        logger.info("Critic reviewing answer (length=%d) with %d evidence chunks", len(answer), len(evidence))
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
            result = CriticResult(
                is_grounded=bool(data.get("is_grounded", False)),
                is_relevant=bool(data.get("is_relevant", False)),
                needs_revision=bool(data.get("needs_revision", False)),
                comment=str(data.get("comment", "No critic comment.")).strip(),
            )
            logger.info("Critic result: grounded=%s, relevant=%s, needs_revision=%s",
                result.is_grounded, result.is_relevant, result.needs_revision)
            return result
        except Exception as e:
            logger.warning("Critic review failed: %s", e)
            return CriticResult(
                is_grounded=False,
                is_relevant=True,
                needs_revision=False,
                comment="Critic output could not be parsed.",
            )