"""Shared pydantic models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FeatureFlags(BaseModel):
    hybrid_retrieval: bool
    cross_encoder_reranking: bool
    query_decomposition: bool
    iterative_retrieval: bool
    self_rag: bool
    evidence_filtering: bool
    evidence_sufficiency: bool
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


class EvidenceSufficiencyResult(BaseModel):
    is_sufficient: bool
    missing_aspects: list[str] = Field(default_factory=list)
    follow_up_queries: list[str] = Field(default_factory=list)
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


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int = 0
    calls: int = 0


class LLMCallUsage(BaseModel):
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int = 0
    usage_available: bool = False
    prompt_chars: int = 0
    completion_chars: int = 0


class PerformanceSpan(BaseModel):
    name: str
    duration_ms: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class PerformanceReport(BaseModel):
    total_duration_ms: float
    spans: list[PerformanceSpan] = Field(default_factory=list)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    llm_calls: list[LLMCallUsage] = Field(default_factory=list)


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
    performance: PerformanceReport | None = None
