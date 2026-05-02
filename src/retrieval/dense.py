"""Dense retrieval with sentence-transformers embeddings."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from src.models import ChunkEvidence


@lru_cache(maxsize=2)
def get_embedding_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class DenseRetriever:
    def __init__(self, model_name: str, evidence: list[ChunkEvidence]) -> None:
        self.model = get_embedding_model(model_name)
        self.evidence = evidence
        self.chunk_texts = [item.text for item in evidence]
        self.chunk_embeddings = self.model.encode(self.chunk_texts, normalize_embeddings=True) if self.chunk_texts else np.array([])

    def score(self, query_text: str) -> list[float]:
        if len(self.evidence) == 0:
            return []
        query_embedding = self.model.encode([query_text], normalize_embeddings=True)[0]
        sims = np.dot(self.chunk_embeddings, query_embedding)
        return [float(x) for x in sims]
