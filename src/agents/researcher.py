"""Research agent: search, chunk, retrieve, rerank, filter."""

from __future__ import annotations

import logging
from collections import OrderedDict

from src.config import Settings
from src.models import ChunkEvidence, IterationLog, SearchResult
from src.retrieval.chunking import chunk_text, deduplicate_chunks
from src.retrieval.dense import DenseRetriever
from src.retrieval.hybrid import apply_hybrid_scores
from src.retrieval.rerank import CrossEncoderReranker
from src.retrieval.sparse import SparseRetriever
from src.retrieval.web_search import TavilySearcher
from src.utils.text import simple_tokens

logger = logging.getLogger(__name__)


class ResearcherAgent:
    def __init__(self, searcher: TavilySearcher, settings: Settings) -> None:
        self.searcher = searcher
        self.settings = settings
        self.reranker = CrossEncoderReranker(settings.cross_encoder_model) if settings.enable_cross_encoder_reranking else None
        logger.info("ResearcherAgent initialized, reranker_enabled=%s", self.reranker is not None)

    def gather_sources(self, queries: list[str]) -> list[SearchResult]:
        logger.info("Gathering sources for %d queries", len(queries))
        merged: OrderedDict[str, SearchResult] = OrderedDict()
        for query in queries:
            logger.debug("Searching for: %s", query)
            for result in self.searcher.search(query):
                if result.url and result.url not in merged:
                    merged[result.url] = result
        logger.info("Gathered %d unique sources", len(merged))
        return list(merged.values())

    def build_chunk_corpus(self, sources: list[SearchResult], query_label: str) -> list[ChunkEvidence]:
        evidence: list[ChunkEvidence] = []
        for source in sources:
            base_text = source.raw_content or source.content
            if not base_text:
                continue
            chunks = deduplicate_chunks(
                chunk_text(base_text, self.settings.chunk_size, self.settings.chunk_overlap)
            )
            for chunk in chunks:
                evidence.append(
                    ChunkEvidence(
                        title=source.title,
                        url=source.url,
                        query=query_label,
                        text=chunk,
                    )
                )
        logger.debug("Built corpus of %d chunks from %d sources", len(evidence), len(sources))
        return evidence

    def simple_score(self, question: str, evidence: list[ChunkEvidence]) -> list[ChunkEvidence]:
        q_tokens = set(simple_tokens(question))
        for item in evidence:
            overlap = len(q_tokens & set(simple_tokens(item.text)))
            item.score_final = float(overlap)
        evidence.sort(key=lambda x: x.score_final, reverse=True)
        return evidence[: self.settings.top_k_chunks]

    def hybrid_retrieve(self, query_text: str, evidence: list[ChunkEvidence]) -> list[ChunkEvidence]:
        if not evidence:
            return []
        sparse = SparseRetriever(evidence)
        dense = DenseRetriever(self.settings.embedding_model, evidence)
        sparse_scores = sparse.score(query_text)
        dense_scores = dense.score(query_text)
        evidence = apply_hybrid_scores(evidence, sparse_scores, dense_scores)
        evidence.sort(key=lambda x: x.score_final, reverse=True)
        return evidence[: self.settings.candidate_pool_size]

    def rerank(self, query_text: str, evidence: list[ChunkEvidence]) -> list[ChunkEvidence]:
        if not evidence:
            return []
        if self.reranker is None:
            evidence.sort(key=lambda x: x.score_final, reverse=True)
            return evidence[: self.settings.rerank_top_k]
        return self.reranker.rerank(query_text, evidence, self.settings.rerank_top_k)

    def run_iteration(
        self,
        question: str,
        queries: list[str],
        retrieval_text: str,
        iteration: int,
    ) -> tuple[list[SearchResult], list[ChunkEvidence], IterationLog]:
        logger.info("Running researcher iteration %d", iteration)
        sources = self.gather_sources(queries)
        corpus = self.build_chunk_corpus(sources, query_label=" | ".join(queries))

        if self.settings.enable_hybrid_retrieval:
            candidates = self.hybrid_retrieve(retrieval_text, corpus)
            logger.info("Hybrid retrieval: %d candidates from %d corpus chunks", len(candidates), len(corpus))
        else:
            candidates = self.simple_score(question, corpus)
            logger.info("Simple scoring: %d candidates from %d corpus chunks", len(candidates), len(corpus))

        if self.settings.enable_cross_encoder_reranking:
            selected = self.rerank(question, candidates)
            logger.info("Cross-encoder reranking: selected %d from %d candidates", len(selected), len(candidates))
        else:
            selected = candidates[: self.settings.rerank_top_k]

        log = IterationLog(
            iteration=iteration,
            queries=queries,
            candidate_count=len(corpus),
            selected_count=len(selected),
            summary=f"Retrieved {len(corpus)} chunks from {len(sources)} sources and kept {len(selected)} chunks for answer generation.",
        )
        return sources, selected, log
