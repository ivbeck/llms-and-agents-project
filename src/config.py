"""Application settings."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    openrouter_api_key: Annotated[str, Field(alias="OPENROUTER_API_KEY")]
    openrouter_model: Annotated[str, Field(default="anthropic/claude-3.5-sonnet", alias="OPENROUTER_MODEL")]
    openrouter_temperature: Annotated[float, Field(default=0.1, alias="OPENROUTER_TEMPERATURE")]
    openrouter_base_url: Annotated[str, Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")]

    tavily_api_key: Annotated[str, Field(alias="TAVILY_API_KEY")]

    embedding_model: Annotated[str, Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")]
    cross_encoder_model: Annotated[str, Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", alias="CROSS_ENCODER_MODEL")]

    max_search_results: int = Field(default=5, alias="MAX_SEARCH_RESULTS")
    top_k_chunks: int = Field(default=8, alias="TOP_K_CHUNKS")
    chunk_size: int = Field(default=1200, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")
    max_iterations: int = Field(default=2, alias="MAX_ITERATIONS")
    max_evidence_retries: int = Field(default=3, alias="MAX_EVIDENCE_RETRIES")
    reflection_steps: int = Field(default=1, alias="REFLECTION_STEPS")
    candidate_pool_size: int = Field(default=20, alias="CANDIDATE_POOL_SIZE")
    rerank_top_k: int = Field(default=8, alias="RERANK_TOP_K")
    filter_top_k: int = Field(default=6, alias="FILTER_TOP_K")

    enable_hybrid_retrieval: bool = Field(default=True, alias="ENABLE_HYBRID_RETRIEVAL")
    enable_cross_encoder_reranking: bool = Field(default=True, alias="ENABLE_CROSS_ENCODER_RERANKING")
    enable_query_decomposition: bool = Field(default=True, alias="ENABLE_QUERY_DECOMPOSITION")
    enable_iterative_retrieval: bool = Field(default=True, alias="ENABLE_ITERATIVE_RETRIEVAL")
    enable_self_rag: bool = Field(default=True, alias="ENABLE_SELF_RAG")
    enable_evidence_filtering: bool = Field(default=True, alias="ENABLE_EVIDENCE_FILTERING")
    enable_evidence_sufficiency: bool = Field(default=True, alias="ENABLE_EVIDENCE_SUFFICIENCY")
    enable_hyde: bool = Field(default=True, alias="ENABLE_HYDE")
    enable_performance_analysis: bool = Field(default=False, alias="ENABLE_PERFORMANCE_ANALYSIS")

    judge_model: Annotated[str, Field(default="openai/gpt-4.1-mini", alias="JUDGE_MODEL")]
    judge_temperature: Annotated[float, Field(default=0.0, alias="JUDGE_TEMPERATURE")]
    ragas_embedding_model: Annotated[str, Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="RAGAS_EMBEDDING_MODEL")]

    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )
