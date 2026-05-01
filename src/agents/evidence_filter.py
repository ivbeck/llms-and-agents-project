"""Evidence filtering agent."""

from __future__ import annotations

from src.llm.openrouter_client import OpenRouterLLM
from src.models import ChunkEvidence
from src.utils.parsing import extract_json_object


class EvidenceFilterAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def filter(self, question: str, evidence: list[ChunkEvidence], top_k: int) -> list[ChunkEvidence]:
        if not evidence:
            return []

        evidence_block = []
        for idx, item in enumerate(evidence, start=1):
            evidence_block.append(
                f"[{idx}] title={item.title}\nurl={item.url}\ntext={item.text}\n"
            )

        system_prompt = (
            "You are an evidence filtering agent in a RAG pipeline. "
            "Keep only chunks that are directly useful for answering the question. "
            "Return only JSON."
        )
        user_prompt = f"""
Question:
{question}

Candidate chunks:
{'\\n'.join(evidence_block)}

Task:
Select the most relevant chunk ids. Remove irrelevant, redundant, or weakly related chunks.
Return JSON only in this format:
{{
  "keep_ids": [1, 3, 5],
  "reason": "short explanation"
}}
"""
        try:
            raw = self.llm.complete(system_prompt, user_prompt)
            data = extract_json_object(raw)
            keep_ids = [int(x) for x in data.get("keep_ids", [])]
            keep = [evidence[i - 1] for i in keep_ids if 1 <= i <= len(evidence)]
            return keep[:top_k] if keep else evidence[:top_k]
        except Exception:
            return evidence[:top_k]