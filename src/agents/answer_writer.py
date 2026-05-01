"""Answer writer agent."""

from __future__ import annotations

from src.llm.openrouter_client import OpenRouterLLM
from src.models import ChunkEvidence


class AnswerWriterAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def write(self, question: str, evidence: list[ChunkEvidence], critique: str | None = None) -> str:
        if not evidence:
            return "I could not find enough reliable evidence to answer the question."

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
        return self.llm.complete(system_prompt, user_prompt).strip()