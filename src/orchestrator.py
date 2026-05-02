"""Main orchestration for baseline and advanced RAG runs."""

from __future__ import annotations

import logging
from collections import OrderedDict

from src.agents.answer_writer import AnswerWriterAgent
from src.agents.critic import CriticAgent
from src.agents.evidence_filter import EvidenceFilterAgent
from src.agents.hyde import HyDEAgent
from src.agents.query_planner import QueryPlannerAgent
from src.agents.researcher import ResearcherAgent
from src.config import Settings
from src.llm.openrouter_client import OpenRouterLLM
from src.models import ChunkEvidence, CriticResult, FeatureFlags, FinalAnswer, SearchResult
from src.retrieval.web_search import TavilySearcher

logger = logging.getLogger(__name__)

class AdvancedMultiAgentRAGSystem:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm = OpenRouterLLM(settings)
        self.searcher = TavilySearcher(settings)

        self.query_planner = QueryPlannerAgent(self.llm)
        self.hyde_agent = HyDEAgent(self.llm)
        self.researcher = ResearcherAgent(self.searcher, settings)
        self.evidence_filter = EvidenceFilterAgent(self.llm)
        self.answer_writer = AnswerWriterAgent(self.llm)
        self.critic = CriticAgent(self.llm)

        logger.info("AdvancedMultiAgentRAGSystem initialized")
        logger.info("Features: hybrid=%s, rerank=%s, query_decomp=%s, iterative=%s, self_rag=%s, evidence_filter=%s, hyde=%s",
            settings.enable_hybrid_retrieval,
            settings.enable_cross_encoder_reranking,
            settings.enable_query_decomposition,
            settings.enable_iterative_retrieval,
            settings.enable_self_rag,
            settings.enable_evidence_filtering,
            settings.enable_hyde,
        )

    def _feature_flags(self) -> FeatureFlags:
        return FeatureFlags(
            hybrid_retrieval=self.settings.enable_hybrid_retrieval,
            cross_encoder_reranking=self.settings.enable_cross_encoder_reranking,
            query_decomposition=self.settings.enable_query_decomposition,
            iterative_retrieval=self.settings.enable_iterative_retrieval,
            self_rag=self.settings.enable_self_rag,
            evidence_filtering=self.settings.enable_evidence_filtering,
            hyde=self.settings.enable_hyde,
        )

    def _merge_sources(self, source_groups: list[list[SearchResult]]) -> list[SearchResult]:
        merged: OrderedDict[str, SearchResult] = OrderedDict()
        for group in source_groups:
            for source in group:
                if source.url and source.url not in merged:
                    merged[source.url] = source
        return list(merged.values())

    def _merge_evidence(self, evidence_groups: list[list[ChunkEvidence]]) -> list[ChunkEvidence]:
        merged: OrderedDict[tuple[str, str], ChunkEvidence] = OrderedDict()
        for group in evidence_groups:
            for item in group:
                key = (item.url, item.text)
                if key not in merged:
                    merged[key] = item
                else:
                    old = merged[key]
                    old.score_sparse = max(old.score_sparse, item.score_sparse)
                    old.score_dense = max(old.score_dense, item.score_dense)
                    old.score_hybrid = max(old.score_hybrid, item.score_hybrid)
                    old.score_rerank = max(old.score_rerank, item.score_rerank)
                    old.score_final = max(old.score_final, item.score_final)
                    if not old.selected_reason and item.selected_reason:
                        old.selected_reason = item.selected_reason
        values = list(merged.values())
        values.sort(key=lambda x: x.score_final, reverse=True)
        return values

    def _advanced_queries(self, question: str) -> list[str]:
        if self.settings.enable_query_decomposition:
            return self.query_planner.decompose(question)
        return [question]

    def answer_question(self, question: str) -> FinalAnswer:
        logger.info("=== Starting pipeline for question: %s", question[:80])
        features = self._feature_flags()
        queries = self._advanced_queries(question)
        logger.info("Query decomposition: %d queries generated", len(queries))
        for i, q in enumerate(queries):
            logger.debug("  Query[%d]: %s", i, q)

        hyde_document = self.hyde_agent.generate(question) if self.settings.enable_hyde else None
        if hyde_document:
            logger.info("HyDE document generated (length=%d)", len(hyde_document))
        else:
            logger.info("HyDE disabled, skipping document generation")

        retrieval_text = question if not hyde_document else f"{question}\n\n{hyde_document}"

        all_sources: list[list[SearchResult]] = []
        all_evidence: list[list[ChunkEvidence]] = []
        ledger = []

        current_queries = queries
        current_answer = ""
        current_critic = CriticResult(
            is_grounded=False,
            is_relevant=True,
            needs_revision=False,
            comment="No critique yet.",
        )

        iterations = self.settings.max_iterations if self.settings.enable_iterative_retrieval else 1
        logger.info("Running %d iteration(s)", iterations)

        for iteration in range(1, iterations + 1):
            logger.info("--- Iteration %d ---", iteration)
            sources, selected, log = self.researcher.run_iteration(
                question=question,
                queries=current_queries,
                retrieval_text=retrieval_text,
                iteration=iteration,
            )
            all_sources.append(sources)
            all_evidence.append(selected)
            ledger.append(log)
            logger.info("Iteration %d: found %d sources, selected %d chunks", iteration, len(sources), len(selected))

            merged_evidence = self._merge_evidence(all_evidence)
            if self.settings.enable_evidence_filtering:
                merged_evidence = self.evidence_filter.filter(question, merged_evidence, self.settings.filter_top_k)
                logger.info("Evidence filtering applied: %d chunks remain", len(merged_evidence))
            else:
                merged_evidence = merged_evidence[: self.settings.top_k_chunks]

            current_answer = self.answer_writer.write(question, merged_evidence)
            logger.info("Answer generated (length=%d)", len(current_answer))
            current_critic = self.critic.review(question, current_answer, merged_evidence)
            logger.info("Critic review: grounded=%s, relevant=%s, needs_revision=%s, comment=%s",
                current_critic.is_grounded,
                current_critic.is_relevant,
                current_critic.needs_revision,
                current_critic.comment,
            )

            if not self.settings.enable_iterative_retrieval:
                logger.info("Iterative retrieval disabled, breaking")
                break
            if iteration >= iterations:
                logger.info("Max iterations reached")
                break
            if not current_critic.needs_revision:
                logger.info("Answer accepted by critic, stopping early")
                break

            follow_up = self.query_planner.next_iteration_queries(
                question=question,
                current_answer=current_answer,
                critique=current_critic.comment,
            )
            if not follow_up:
                logger.info("No follow-up queries generated")
                break
            current_queries = follow_up
            logger.info("Follow-up queries: %s", follow_up)

        logger.info("Merging sources and evidence across all iterations")
        merged_sources = self._merge_sources(all_sources)
        merged_evidence = self._merge_evidence(all_evidence)
        if self.settings.enable_evidence_filtering:
            merged_evidence = self.evidence_filter.filter(question, merged_evidence, self.settings.top_k_chunks)
            logger.info("Final evidence filtering: %d chunks remain", len(merged_evidence))
        else:
            merged_evidence = merged_evidence[: self.settings.top_k_chunks]

        final_answer = current_answer or self.answer_writer.write(question, merged_evidence)
        final_critic = current_critic or self.critic.review(question, final_answer, merged_evidence)

        if self.settings.enable_self_rag:
            logger.info("Running self-RAG reflection loop (%d steps)", self.settings.reflection_steps)
            for step in range(self.settings.reflection_steps):
                if not final_critic.needs_revision:
                    logger.info("Reflection step %d: answer accepted", step + 1)
                    break
                logger.info("Reflection step %d: needs revision, regenerating answer", step + 1)
                final_answer = self.answer_writer.write(question, merged_evidence, critique=final_critic.comment)
                final_critic = self.critic.review(question, final_answer, merged_evidence)

        used_urls = {item.url for item in merged_evidence}
        used_sources = [source for source in merged_sources if source.url in used_urls]

        logger.info("=== Pipeline complete: answer_length=%d, sources=%d, evidence_chunks=%d",
            len(final_answer), len(used_sources), len(merged_evidence))

        return FinalAnswer(
            question=question,
            queries=queries,
            hyde_document=hyde_document,
            answer=final_answer,
            critic=final_critic,
            sources=used_sources,
            evidence=merged_evidence,
            features=features,
            ledger=ledger,
        )
