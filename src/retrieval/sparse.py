"""Sparse retrieval with BM25."""

from __future__ import annotations

from rank_bm25 import BM25Okapi

from src.models import ChunkEvidence
from src.utils.text import simple_tokens


class SparseRetriever:
    def __init__(self, evidence: list[ChunkEvidence]) -> None:
        self.evidence = evidence
        self.corpus_tokens = [simple_tokens(item.text) for item in evidence]
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None

    def score(self, query: str) -> list[float]:
        if self.bm25 is None:
            return [0.0 for _ in self.evidence]
        q_tokens = simple_tokens(query)
        scores = self.bm25.get_scores(q_tokens)
        return [float(s) for s in scores]
