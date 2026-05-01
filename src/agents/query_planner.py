"""Query planner with optional decomposition."""

from __future__ import annotations

import logging

from src.llm.openrouter_client import OpenRouterLLM
from src.utils.parsing import extract_json_object

logger = logging.getLogger(__name__)


class QueryPlannerAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def plan_baseline(self, question: str) -> list[str]:
        return [question]

    def decompose(self, question: str) -> list[str]:
        logger.info("Decomposing question into sub-queries")
        system_prompt = (
            "You are a query planning agent for a RAG system. "
            "Break complex user questions into focused web-search subqueries. "
            "Return only JSON."
        )
        user_prompt = f"""
Generate exactly 4 focused search queries for the question below.
Rules:
- Keep each query concise.
- Each query should cover a different aspect of the question.
- Queries should be retrieval-friendly.
- Return JSON only:
{{
  "queries": ["...", "...", "...", "..."]
}}

Question:
{question}
"""
        raw = self.llm.complete(system_prompt, user_prompt)
        data = extract_json_object(raw)
        queries = [str(x).strip() for x in data.get("queries", []) if str(x).strip()]
        result = queries[:4] if queries else [question]
        logger.info("Decomposed into %d queries", len(result))
        return result

    def next_iteration_queries(self, question: str, current_answer: str, critique: str) -> list[str]:
        system_prompt = (
            "You are a retrieval-gap analysis agent. "
            "Given a question, a partial answer, and critique, propose follow-up web-search queries. "
            "Return only JSON."
        )
        user_prompt = f"""
Generate up to 3 new focused search queries that would help fill remaining information gaps.
Return JSON only:
{{
  "queries": ["...", "...", "..."]
}}

Question:
{question}

Current answer:
{current_answer}

Critique / missing points:
{critique}
"""
        raw = self.llm.complete(system_prompt, user_prompt)
        data = extract_json_object(raw)
        queries = [str(x).strip() for x in data.get("queries", []) if str(x).strip()]
        return queries[:3]