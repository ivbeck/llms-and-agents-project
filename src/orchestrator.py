"""Main orchestration for baseline and advanced RAG runs."""

from __future__ import annotations

from collections import OrderedDict

from src.agents.answer_writer import AnswerWriterAgent
from src.agents.critic import CriticAgent
from src.agents.evidence_filter import EvidenceFilterAgent
from src.agents.hyde import HyDEAgent
from src.agents.query_planner import QueryPlannerAgent
from src.agents.researcher import ResearcherAgent
from src.config import Settings
from src.llm.groq_client import GroqLLM
from src.models import ChunkEvidence, CriticResult, FeatureFlags, FinalAnswer, SearchResult
from src.retrieval.web_search import TavilySearcher


class AdvancedMultiAgentRAGSystem:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm = GroqLLM(settings)
        self.searcher = TavilySearcher(settings)

        self.query_planner = QueryPlannerAgent(self.llm)
        self.hyde_agent = HyDEAgent(self.llm)
        self.researcher = ResearcherAgent(self.searcher, settings)
        self.evidence_filter = EvidenceFilterAgent(self.llm)
        self.answer_writer = AnswerWriterAgent(self.llm)
        self.critic = CriticAgent(self.llm)

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
        values = list(merged.values())
        values.sort(key=lambda x: x.score_final, reverse=True)
        return values

    def _advanced_queries(self, question: str) -> list[str]:
        if self.settings.enable_query_decomposition:
            return self.query_planner.decompose(question)
        return [question]

    def answer_question(self, question: str) -> FinalAnswer:
        features = self._feature_flags()
        queries = self._advanced_queries(question)
        hyde_document = self.hyde_agent.generate(question) if self.settings.enable_hyde else None
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

        for iteration in range(1, iterations + 1):
            sources, selected, log = self.researcher.run_iteration(
                question=question,
                queries=current_queries,
                retrieval_text=retrieval_text,
                iteration=iteration,
            )
            all_sources.append(sources)
            all_evidence.append(selected)
            ledger.append(log)

            merged_evidence = self._merge_evidence(all_evidence)
            if self.settings.enable_evidence_filtering:
                merged_evidence = self.evidence_filter.filter(question, merged_evidence, self.settings.filter_top_k)
            else:
                merged_evidence = merged_evidence[: self.settings.top_k_chunks]

            current_answer = self.answer_writer.write(question, merged_evidence)
            current_critic = self.critic.review(question, current_answer, merged_evidence)

            if not self.settings.enable_iterative_retrieval:
                break
            if iteration >= iterations:
                break
            if not current_critic.needs_revision:
                break

            follow_up = self.query_planner.next_iteration_queries(
                question=question,
                current_answer=current_answer,
                critique=current_critic.comment,
            )
            if not follow_up:
                break
            current_queries = follow_up

        merged_sources = self._merge_sources(all_sources)
        merged_evidence = self._merge_evidence(all_evidence)
        if self.settings.enable_evidence_filtering:
            merged_evidence = self.evidence_filter.filter(question, merged_evidence, self.settings.top_k_chunks)
        else:
            merged_evidence = merged_evidence[: self.settings.top_k_chunks]

        final_answer = current_answer or self.answer_writer.write(question, merged_evidence)
        final_critic = current_critic or self.critic.review(question, final_answer, merged_evidence)

        if self.settings.enable_self_rag:
            for _ in range(self.settings.reflection_steps):
                if not final_critic.needs_revision:
                    break
                final_answer = self.answer_writer.write(question, merged_evidence, critique=final_critic.comment)
                final_critic = self.critic.review(question, final_answer, merged_evidence)

        used_urls = {item.url for item in merged_evidence}
        used_sources = [source for source in merged_sources if source.url in used_urls]

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
