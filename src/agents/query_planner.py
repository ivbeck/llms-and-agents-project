"""Query planner with optional decomposition."""

from __future__ import annotations

import logging

from src.llm.openrouter_client import OpenRouterLLM
from src.models import QueryPlanResult
from src.utils.parsing import extract_json_object

logger = logging.getLogger(__name__)


class QueryPlannerAgent:
    def __init__(self, llm: OpenRouterLLM) -> None:
        self.llm = llm

    def plan_baseline(self, question: str) -> list[str]:
        return [question]

    def plan(self, question: str, max_queries: int = 4, default_search_depth: str = "advanced") -> QueryPlanResult:
        logger.info("Decomposing question into sub-queries")
        max_queries = max(1, max_queries)
        system_prompt = (
            "You are a query planning agent for a RAG system. "
            "Break user questions into focused web-search subqueries and choose a Tavily search depth. "
            "Return only JSON."
        )
        user_prompt = f"""
Generate between 1 and {max_queries} focused search queries for the question below.
Rules:
- Keep each query concise.
- Use fewer queries for simple factual questions.
- Use more queries only when the question has multiple aspects, ambiguous entities, or requires current/confirming evidence.
- Each query should cover a different aspect of the question when multiple queries are needed.
- Queries should be retrieval-friendly.
- Choose "basic" search_depth for simple factual lookup or broad orientation.
- Choose "advanced" search_depth for ambiguous, current, source-sensitive, multi-step, or evidence-critical questions.
- Return JSON only:
{{
  "queries": ["...", "..."],
  "search_depth": "basic"
}}

Question:
{question}
"""
        try:
            raw = self.llm.complete(system_prompt, user_prompt)
            parsed = extract_json_object(raw)
            if isinstance(parsed, dict) and "search_depth" in parsed:
                parsed["search_depth"] = str(parsed["search_depth"]).strip().lower()
            data = QueryPlanResult.model_validate(parsed)
        except Exception as exc:
            logger.warning("Query decomposition failed: %s", exc)
            fallback_depth = default_search_depth if default_search_depth in {"basic", "advanced"} else "advanced"
            return QueryPlanResult(queries=[question], search_depth=fallback_depth)

        queries = [str(x).strip() for x in data.queries if str(x).strip()]
        result = QueryPlanResult(
            queries=queries[:max_queries] if queries else [question],
            search_depth=data.search_depth,
        )
        logger.info("Decomposed into %d queries with search_depth=%s", len(result.queries), result.search_depth)
        return result

    def decompose(self, question: str, max_queries: int = 4) -> list[str]:
        return self.plan(question, max_queries=max_queries).queries

    def next_iteration_plan(
        self,
        question: str,
        current_answer: str,
        critique: str,
        default_search_depth: str = "advanced",
    ) -> QueryPlanResult:
        system_prompt = (
            "You are a retrieval-gap analysis agent. "
            "Given a question, a partial answer, and critique, propose follow-up web-search queries and choose a Tavily search depth. "
            "Return only JSON."
        )
        user_prompt = f"""
Generate up to 3 new focused search queries that would help fill remaining information gaps.
Choose "basic" search_depth if the missing point is simple to verify.
Choose "advanced" search_depth if the missing point needs precise, current, or source-sensitive evidence.
Return JSON only:
{{
  "queries": ["...", "...", "..."],
  "search_depth": "advanced"
}}

Question:
{question}

Current answer:
{current_answer}

Critique / missing points:
{critique}
"""
        try:
            raw = self.llm.complete(system_prompt, user_prompt)
            parsed = extract_json_object(raw)
            if isinstance(parsed, dict) and "search_depth" in parsed:
                parsed["search_depth"] = str(parsed["search_depth"]).strip().lower()
            data = QueryPlanResult.model_validate(parsed)
        except Exception as exc:
            logger.warning("Follow-up query generation failed: %s", exc)
            fallback_depth = default_search_depth if default_search_depth in {"basic", "advanced"} else "advanced"
            return QueryPlanResult(queries=[], search_depth=fallback_depth)

        queries = [str(x).strip() for x in data.queries if str(x).strip()]
        return QueryPlanResult(queries=queries[:3], search_depth=data.search_depth)

    def next_iteration_queries(self, question: str, current_answer: str, critique: str) -> list[str]:
        return self.next_iteration_plan(question, current_answer, critique).queries
