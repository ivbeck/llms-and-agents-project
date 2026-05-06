"""Cross-encoder reranking."""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import CrossEncoder

from src.models import ChunkEvidence


@lru_cache(maxsize=2)
def get_cross_encoder(model_name: str) -> CrossEncoder:
    return CrossEncoder(model_name)


class CrossEncoderReranker:
    def __init__(self, model_name: str) -> None:
        self.model = get_cross_encoder(model_name)

    def rerank(self, query: str, evidence: list[ChunkEvidence], top_k: int) -> list[ChunkEvidence]:
        if not evidence:
            return []
        pairs = [(query, item.text) for item in evidence]
        scores = self.model.predict(pairs)
        for item, score in zip(evidence, scores):
            item.score_rerank = float(score)
            item.score_final = float(score)
        evidence.sort(key=lambda x: x.score_final, reverse=True)
        return evidence[:top_k]
