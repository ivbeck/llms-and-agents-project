"""Main orchestration for baseline and advanced RAG runs."""

from __future__ import annotations

import logging
from collections import OrderedDict

from src.agents.answer_writer import AnswerWriterAgent
from src.agents.critic import CriticAgent
from src.agents.evidence_filter import EvidenceFilterAgent
from src.agents.evidence_sufficiency import EvidenceSufficiencyAgent
from src.agents.hyde import HyDEAgent
from src.agents.query_planner import QueryPlannerAgent
from src.agents.researcher import ResearcherAgent
from src.config import Settings
from src.llm.openrouter_client import OpenRouterLLM
from src.models import ChunkEvidence, CriticResult, FeatureFlags, FinalAnswer, QueryPlanResult, SearchResult
from src.performance import PerformanceTracker, log_performance_report
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
        self.evidence_sufficiency = EvidenceSufficiencyAgent(self.llm)
        self.answer_writer = AnswerWriterAgent(self.llm)
        self.critic = CriticAgent(self.llm)

        logger.info("AdvancedMultiAgentRAGSystem initialized")
        logger.info("Features: hybrid=%s, rerank=%s, query_decomp=%s, iterative=%s, self_rag=%s, evidence_filter=%s, evidence_sufficiency=%s, hyde=%s",
            settings.enable_hybrid_retrieval,
            settings.enable_cross_encoder_reranking,
            settings.enable_query_decomposition,
            settings.enable_iterative_retrieval,
            settings.enable_self_rag,
            settings.enable_evidence_filtering,
            settings.enable_evidence_sufficiency,
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
            evidence_sufficiency=self.settings.enable_evidence_sufficiency,
            hyde=self.settings.enable_hyde,
        )

    def _prepare_evidence(
        self,
        question: str,
        all_evidence: list[list[ChunkEvidence]],
        iteration: int,
        tracker: PerformanceTracker,
    ) -> list[ChunkEvidence]:
        with tracker.span("evidence.merge", iteration=iteration, evidence_groups=len(all_evidence)) as meta:
            merged_evidence = self._merge_evidence(all_evidence)
            meta["merged_count"] = len(merged_evidence)
        if self.settings.enable_evidence_filtering:
            with tracker.span("evidence_filter", iteration=iteration, input_count=len(merged_evidence), top_k=self.settings.filter_top_k) as meta:
                merged_evidence = self.evidence_filter.filter(question, merged_evidence, self.settings.filter_top_k)
                meta["output_count"] = len(merged_evidence)
            logger.info("Evidence filtering applied: %d chunks remain", len(merged_evidence))
        else:
            merged_evidence = merged_evidence[: self.settings.top_k_chunks]
        return self._renumber_evidence(merged_evidence)

    @staticmethod
    def _renumber_evidence(evidence: list[ChunkEvidence]) -> list[ChunkEvidence]:
        """Reassign contiguous E1, E2, ... ids so downstream agents and judges see
        a clean pool. Chunk-level ids from the researcher corpus are non-contiguous
        after filtering and can collide across iterations, which causes the answer
        writer to cite ids that don't exist (e.g. [E1] when only E2 survived)."""
        for idx, item in enumerate(evidence, start=1):
            item.evidence_id = f"E{idx}"
        return evidence

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

    def _advanced_query_plan(self, question: str) -> QueryPlanResult:
        if self.settings.enable_query_decomposition:
            return self.query_planner.plan(
                question,
                max_queries=self.settings.max_query_decomposition_queries,
                default_search_depth=self.settings.tavily_default_search_depth,
            )
        return QueryPlanResult(
            queries=[question],
            search_depth=self.settings.tavily_default_search_depth,
        )

    def _advanced_queries(self, question: str) -> list[str]:
        return self._advanced_query_plan(question).queries

    def answer_question(self, question: str) -> FinalAnswer:
        tracker = PerformanceTracker(self.settings.enable_performance_analysis)
        self.llm.usage_callback = tracker.record_llm_call
        try:
            with tracker.span("pipeline.total", question_chars=len(question)):
                result = self._answer_question(question, tracker)
            result.performance = tracker.finish()
        finally:
            self.llm.usage_callback = None
        log_performance_report(result.performance)
        return result

    def _answer_question(self, question: str, tracker: PerformanceTracker) -> FinalAnswer:
        logger.info("=== Starting pipeline for question: %s", question[:80])
        features = self._feature_flags()
        with tracker.span("query_decomposition", enabled=self.settings.enable_query_decomposition) as meta:
            initial_plan = self._advanced_query_plan(question)
            queries = initial_plan.queries
            current_search_depth = initial_plan.search_depth
            meta["query_count"] = len(queries)
            meta["search_depth"] = current_search_depth
        logger.info("Query decomposition: %d queries generated, search_depth=%s", len(queries), current_search_depth)
        for i, q in enumerate(queries):
            logger.debug("  Query[%d]: %s", i, q)

        with tracker.span("hyde_generation", enabled=self.settings.enable_hyde) as meta:
            hyde_document = self.hyde_agent.generate(question) if self.settings.enable_hyde else None
            meta["document_chars"] = len(hyde_document or "")
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
            with tracker.span("iteration.total", iteration=iteration, query_count=len(current_queries), search_depth=current_search_depth) as iteration_meta:
                logger.info("--- Iteration %d ---", iteration)
                sources, selected, log = self.researcher.run_iteration(
                    question=question,
                    queries=current_queries,
                    retrieval_text=retrieval_text,
                    iteration=iteration,
                    search_depth=current_search_depth,
                    tracker=tracker,
                )
                all_sources.append(sources)
                all_evidence.append(selected)
                ledger.append(log)
                iteration_meta["source_count"] = len(sources)
                iteration_meta["selected_count"] = len(selected)
                logger.info("Iteration %d: found %d sources, selected %d chunks", iteration, len(sources), len(selected))

                merged_evidence = self._prepare_evidence(question, all_evidence, iteration, tracker)
                evidence_retry_count = 0
                while self.settings.enable_evidence_sufficiency:
                    with tracker.span(
                        "evidence_sufficiency",
                        iteration=iteration,
                        retry=evidence_retry_count,
                        evidence_count=len(merged_evidence),
                    ) as meta:
                        sufficiency = self.evidence_sufficiency.review(question, merged_evidence)
                        meta["is_sufficient"] = sufficiency.is_sufficient
                        meta["follow_up_query_count"] = len(sufficiency.follow_up_queries)
                    if sufficiency.is_sufficient:
                        logger.info("Evidence sufficiency accepted: %s", sufficiency.reason)
                        break
                    if evidence_retry_count >= self.settings.max_evidence_retries:
                        logger.info(
                            "Evidence sufficiency max retries reached (%d): %s",
                            self.settings.max_evidence_retries,
                            sufficiency.reason,
                        )
                        break
                    if not sufficiency.follow_up_queries:
                        logger.info("Evidence insufficient but no sufficiency follow-up queries were generated")
                        break

                    evidence_retry_count += 1
                    logger.info(
                        "Evidence insufficient; running sufficiency retry %d/%d with queries: %s",
                        evidence_retry_count,
                        self.settings.max_evidence_retries,
                        sufficiency.follow_up_queries,
                    )
                    retry_sources, retry_selected, retry_log = self.researcher.run_iteration(
                        question=question,
                        queries=sufficiency.follow_up_queries,
                        retrieval_text=retrieval_text,
                        iteration=iteration,
                        search_depth="advanced",
                        tracker=tracker,
                    )
                    all_sources.append(retry_sources)
                    all_evidence.append(retry_selected)
                    retry_log.summary = (
                        f"Evidence sufficiency retry {evidence_retry_count}: "
                        f"{retry_log.summary}"
                    )
                    ledger.append(retry_log)
                    merged_evidence = self._prepare_evidence(question, all_evidence, iteration, tracker)
                iteration_meta["evidence_retry_count"] = evidence_retry_count

                with tracker.span("answer_write", iteration=iteration, evidence_count=len(merged_evidence)) as meta:
                    current_answer = self.answer_writer.write(question, merged_evidence)
                    meta["answer_chars"] = len(current_answer)
                logger.info("Answer generated (length=%d)", len(current_answer))
                with tracker.span("critic_review", iteration=iteration, evidence_count=len(merged_evidence), answer_chars=len(current_answer)) as meta:
                    current_critic = self.critic.review(question, current_answer, merged_evidence)
                    meta["needs_revision"] = current_critic.needs_revision
                    meta["is_grounded"] = current_critic.is_grounded
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

            with tracker.span("follow_up_query_generation", iteration=iteration) as meta:
                follow_up_plan = self.query_planner.next_iteration_plan(
                    question=question,
                    current_answer=current_answer,
                    critique=current_critic.comment,
                    default_search_depth=self.settings.tavily_default_search_depth,
                )
                follow_up = follow_up_plan.queries
                meta["query_count"] = len(follow_up)
                meta["search_depth"] = follow_up_plan.search_depth
            if not follow_up:
                logger.info("No follow-up queries generated")
                break
            current_queries = follow_up
            current_search_depth = follow_up_plan.search_depth
            logger.info("Follow-up queries: %s, search_depth=%s", follow_up, current_search_depth)

        logger.info("Merging sources and evidence across all iterations")
        with tracker.span("final_merge", source_groups=len(all_sources), evidence_groups=len(all_evidence)) as meta:
            merged_sources = self._merge_sources(all_sources)
            merged_evidence = self._merge_evidence(all_evidence)
            meta["source_count"] = len(merged_sources)
            meta["evidence_count"] = len(merged_evidence)
        if self.settings.enable_evidence_filtering:
            with tracker.span("final_evidence_filter", input_count=len(merged_evidence), top_k=self.settings.top_k_chunks) as meta:
                merged_evidence = self.evidence_filter.filter(question, merged_evidence, self.settings.top_k_chunks)
                meta["output_count"] = len(merged_evidence)
            logger.info("Final evidence filtering: %d chunks remain", len(merged_evidence))
        else:
            merged_evidence = merged_evidence[: self.settings.top_k_chunks]
        merged_evidence = self._renumber_evidence(merged_evidence)

        if current_answer:
            final_answer = current_answer
        else:
            with tracker.span("final_answer_write", evidence_count=len(merged_evidence)) as meta:
                final_answer = self.answer_writer.write(question, merged_evidence)
                meta["answer_chars"] = len(final_answer)
        final_critic = current_critic or self.critic.review(question, final_answer, merged_evidence)

        if self.settings.enable_self_rag:
            logger.info("Running self-RAG reflection loop (%d steps)", self.settings.reflection_steps)
            for step in range(self.settings.reflection_steps):
                if not final_critic.needs_revision:
                    logger.info("Reflection step %d: answer accepted", step + 1)
                    break
                logger.info("Reflection step %d: needs revision, regenerating answer", step + 1)
                with tracker.span("self_rag.answer_write", step=step + 1, evidence_count=len(merged_evidence)) as meta:
                    final_answer = self.answer_writer.write(question, merged_evidence, critique=final_critic.comment)
                    meta["answer_chars"] = len(final_answer)
                with tracker.span("self_rag.critic_review", step=step + 1, evidence_count=len(merged_evidence), answer_chars=len(final_answer)) as meta:
                    final_critic = self.critic.review(question, final_answer, merged_evidence)
                    meta["needs_revision"] = final_critic.needs_revision

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
