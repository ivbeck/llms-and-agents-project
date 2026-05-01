"""Answer writer agent."""

from __future__ import annotations

import logging

from src.llm.openrouter_client import OpenRouterLLM
from src.models import ChunkEvidence

logger = logging.getLogger(__name__)


class AnswerWriterAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def write(self, question: str, evidence: list[ChunkEvidence], critique: str | None = None) -> str:
        if not evidence:
            logger.warning("No evidence provided to answer writer, returning fallback answer")
            return "I could not find enough reliable evidence to answer the question."

        logger.info("Writing answer with %d evidence chunks", len(evidence))

        evidence_block = []
        for idx, item in enumerate(evidence, start=1):
            evidence_block.append(
                f"[Evidence {idx}]\n"
                f"Title: {item.title}\n"
                f"URL: {item.url}\n"
                f"Text: {item.text}\n"
            )

        improvement = f"\nCritique to address:\n{critique}\n" if critique else ""
        system_prompt = (
            "You are an answer-writing agent in a retrieval-augmented QA system. "
            "Use only the provided evidence. Do not invent unsupported facts."
        )
        user_prompt = f"""
Answer the question using ONLY the evidence below.
Requirements:
- Give a concise but complete answer.
- If evidence is incomplete, say so.
- End with a short section titled: Why these sources were relevant.
- Do not mention any information not supported by evidence.
{improvement}
Question:
{question}

Evidence:
{'\\n'.join(evidence_block)}
"""
        result = self.llm.complete(system_prompt, user_prompt).strip()
        logger.info("Answer written, length=%d", len(result))
        return result