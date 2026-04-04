"""Hybrid retrieval and score fusion."""

from __future__ import annotations

from src.models import ChunkEvidence


def minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[float]:
    if not rankings:
        return []
    size = len(rankings[0])
    scores = [0.0 for _ in range(size)]
    for ranking in rankings:
        for rank, idx in enumerate(ranking, start=1):
            scores[idx] += 1.0 / (k + rank)
    return scores


def apply_hybrid_scores(evidence: list[ChunkEvidence], sparse_scores: list[float], dense_scores: list[float]) -> list[ChunkEvidence]:
    sparse_norm = minmax(sparse_scores)
    dense_norm = minmax(dense_scores)

    sparse_rank = sorted(range(len(evidence)), key=lambda i: sparse_scores[i], reverse=True)
    dense_rank = sorted(range(len(evidence)), key=lambda i: dense_scores[i], reverse=True)
    rrf_scores = reciprocal_rank_fusion([sparse_rank, dense_rank])
    rrf_norm = minmax(rrf_scores)

    updated: list[ChunkEvidence] = []
    for i, item in enumerate(evidence):
        item.score_sparse = sparse_scores[i] if i < len(sparse_scores) else 0.0
        item.score_dense = dense_scores[i] if i < len(dense_scores) else 0.0
        item.score_hybrid = 0.4 * sparse_norm[i] + 0.4 * dense_norm[i] + 0.2 * rrf_norm[i]
        item.score_final = item.score_hybrid
        updated.append(item)
    return updated
