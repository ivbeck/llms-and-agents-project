"""Application settings."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    tavily_api_key: str = Field(alias="TAVILY_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    groq_temperature: float = Field(default=0.1, alias="GROQ_TEMPERATURE")

    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    cross_encoder_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", alias="CROSS_ENCODER_MODEL")

    max_search_results: int = Field(default=5, alias="MAX_SEARCH_RESULTS")
    top_k_chunks: int = Field(default=8, alias="TOP_K_CHUNKS")
    chunk_size: int = Field(default=1200, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")
    max_iterations: int = Field(default=2, alias="MAX_ITERATIONS")
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
    enable_hyde: bool = Field(default=True, alias="ENABLE_HYDE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )
