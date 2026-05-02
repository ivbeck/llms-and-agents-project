"""Shared pydantic models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FeatureFlags(BaseModel):
    hybrid_retrieval: bool
    cross_encoder_reranking: bool
    query_decomposition: bool
    iterative_retrieval: bool
    self_rag: bool
    evidence_filtering: bool
    hyde: bool


class SearchResult(BaseModel):
    title: str
    url: str
    content: str = ""
    raw_content: str = ""


class ChunkEvidence(BaseModel):
    evidence_id: str = ""
    title: str
    url: str
    query: str
    text: str
    selected_reason: str | None = None
    score_sparse: float = 0.0
    score_dense: float = 0.0
    score_hybrid: float = 0.0
    score_rerank: float = 0.0
    score_final: float = 0.0


class QueryPlanResult(BaseModel):
    queries: list[str] = Field(default_factory=list)


class EvidenceKeepItem(BaseModel):
    id: int
    reason: str = ""


class EvidenceFilterResult(BaseModel):
    keep: list[EvidenceKeepItem] = Field(default_factory=list)
    reason: str = ""


class CriticResult(BaseModel):
    is_grounded: bool
    is_relevant: bool
    needs_revision: bool
    comment: str


class IterationLog(BaseModel):
    iteration: int
    queries: list[str]
    candidate_count: int
    selected_count: int
    summary: str


class FinalAnswer(BaseModel):
    question: str
    queries: list[str]
    hyde_document: str | None = None
    answer: str
    critic: CriticResult
    sources: list[SearchResult]
    evidence: list[ChunkEvidence]
    features: FeatureFlags
    ledger: list[IterationLog] = Field(default_factory=list)
