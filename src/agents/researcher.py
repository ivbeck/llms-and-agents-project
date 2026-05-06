"""Research agent: search, chunk, retrieve, rerank, filter."""

from __future__ import annotations

import logging
from collections import OrderedDict
from contextlib import contextmanager

from src.config import Settings
from src.models import ChunkEvidence, IterationLog, SearchResult
from src.performance import PerformanceTracker
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

    def gather_sources(self, queries: list[str], tracker: PerformanceTracker | None = None) -> list[SearchResult]:
        logger.info("Gathering sources for %d queries", len(queries))
        merged: OrderedDict[str, SearchResult] = OrderedDict()
        span = tracker.span if tracker else None
        for query in queries:
            logger.debug("Searching for: %s", query)
            context = span("web_search.query", query=query[:120]) if span else None
            if context is None:
                try:
                    results = self.searcher.search(query)
                except Exception as exc:
                    logger.warning("Search failed for query '%s': %s", query, exc)
                    continue
            else:
                with context as meta:
                    try:
                        results = self.searcher.search(query)
                    except Exception as exc:
                        logger.warning("Search failed for query '%s': %s", query, exc)
                        meta["failed"] = True
                        meta["error_type"] = type(exc).__name__
                        continue
                    meta["result_count"] = len(results)
                    meta["raw_content_chars"] = sum(len(item.raw_content or "") for item in results)
            for result in results:
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
                        evidence_id=f"E{len(evidence) + 1}",
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

    def hybrid_retrieve(self, query_text: str, evidence: list[ChunkEvidence], tracker: PerformanceTracker | None = None) -> list[ChunkEvidence]:
        if not evidence:
            return []
        sparse = SparseRetriever(evidence)
        with tracker.span("retrieval.sparse_score", chunk_count=len(evidence)) if tracker else _null_span() as meta:
            sparse_scores = sparse.score(query_text)
            meta["score_count"] = len(sparse_scores)
        with tracker.span("retrieval.dense_embedding", chunk_count=len(evidence), model=self.settings.embedding_model) if tracker else _null_span() as meta:
            dense = DenseRetriever(self.settings.embedding_model, evidence)
            dense_scores = dense.score(query_text)
            meta["score_count"] = len(dense_scores)
        evidence = apply_hybrid_scores(evidence, sparse_scores, dense_scores)
        evidence.sort(key=lambda x: x.score_final, reverse=True)
        return evidence[: self.settings.candidate_pool_size]

    def rerank(self, query_text: str, evidence: list[ChunkEvidence], tracker: PerformanceTracker | None = None) -> list[ChunkEvidence]:
        if not evidence:
            return []
        if self.reranker is None:
            evidence.sort(key=lambda x: x.score_final, reverse=True)
            return evidence[: self.settings.rerank_top_k]
        with tracker.span("retrieval.cross_encoder_rerank", candidate_count=len(evidence), top_k=self.settings.rerank_top_k, model=self.settings.cross_encoder_model) if tracker else _null_span() as meta:
            result = self.reranker.rerank(query_text, evidence, self.settings.rerank_top_k)
            meta["selected_count"] = len(result)
            return result

    def run_iteration(
        self,
        question: str,
        queries: list[str],
        retrieval_text: str,
        iteration: int,
        tracker: PerformanceTracker | None = None,
    ) -> tuple[list[SearchResult], list[ChunkEvidence], IterationLog]:
        logger.info("Running researcher iteration %d", iteration)
        with tracker.span("researcher.web_search.total", iteration=iteration, query_count=len(queries)) if tracker else _null_span() as meta:
            sources = self.gather_sources(queries, tracker=tracker)
            meta["source_count"] = len(sources)
        with tracker.span("researcher.chunking", iteration=iteration, source_count=len(sources)) if tracker else _null_span() as meta:
            corpus = self.build_chunk_corpus(sources, query_label=" | ".join(queries))
            meta["chunk_count"] = len(corpus)
            meta["source_text_chars"] = sum(len(source.raw_content or source.content or "") for source in sources)

        if self.settings.enable_hybrid_retrieval:
            with tracker.span("researcher.hybrid_retrieval.total", iteration=iteration, chunk_count=len(corpus)) if tracker else _null_span() as meta:
                candidates = self.hybrid_retrieve(retrieval_text, corpus, tracker=tracker)
                meta["candidate_count"] = len(candidates)
            logger.info("Hybrid retrieval: %d candidates from %d corpus chunks", len(candidates), len(corpus))
        else:
            with tracker.span("researcher.simple_score", iteration=iteration, chunk_count=len(corpus)) if tracker else _null_span() as meta:
                candidates = self.simple_score(question, corpus)
                meta["candidate_count"] = len(candidates)
            logger.info("Simple scoring: %d candidates from %d corpus chunks", len(candidates), len(corpus))

        if self.settings.enable_cross_encoder_reranking:
            selected = self.rerank(question, candidates, tracker=tracker)
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


@contextmanager
def _null_span():
    yield {}
