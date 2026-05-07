"""RAGAS metric wrappers: faithfulness, answer relevancy, context precision/recall.

Faithfulness and answer relevancy work with no gold answer; context precision
and context recall require `reference` (gold). Each metric is computed per
sample so this composes cleanly with score.py incremental output.

ragas is imported lazily so the project still works when it is not installed.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from src.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class RagasScores:
    faithfulness: float | None = None
    answer_relevancy: float | None = None
    context_precision: float | None = None
    context_recall: float | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "faithfulness": self.faithfulness,
            "answer_relevancy": self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall": self.context_recall,
            "error": self.error,
        }


class _STEmbeddings:
    """Minimal LangChain-compatible Embeddings wrapper around sentence-transformers.

    We avoid pulling langchain-community just for this; ragas only needs
    embed_documents / embed_query.
    """

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(list(texts), normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self._model.encode([text], normalize_embeddings=True)[0].tolist()


@lru_cache(maxsize=1)
def _get_embeddings(model_name: str) -> Any:
    from ragas.embeddings import LangchainEmbeddingsWrapper

    return LangchainEmbeddingsWrapper(_STEmbeddings(model_name))


@lru_cache(maxsize=1)
def _get_llm_wrapper(judge_model: str, base_url: str, api_key: str, temperature: float) -> Any:
    """RAGAS' AnswerRelevancy passes `n=...` to draw multiple question candidates,
    which langchain-openrouter's client rejects. Use langchain-openai's ChatOpenAI
    pointed at OpenRouter's OpenAI-compatible endpoint instead — same provider,
    native `n` support.
    """
    from langchain_openai import ChatOpenAI
    from ragas.llms import LangchainLLMWrapper

    chat = ChatOpenAI(
        api_key=api_key,
        model=judge_model,
        temperature=temperature,
        base_url=base_url,
    )
    return LangchainLLMWrapper(chat)


class RagasEvaluator:
    """Compute RAGAS metrics for a single (question, answer, contexts, gold) sample."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._llm = None
        self._embeddings = None
        self._metrics: dict[str, Any] = {}

    def _ensure_loaded(self) -> None:
        if self._llm is not None:
            return
        try:
            from ragas.metrics import (
                AnswerRelevancy,
                ContextPrecision,
                ContextRecall,
                Faithfulness,
            )
        except ImportError as exc:
            raise RuntimeError(
                "ragas is not installed. Install with `pip install ragas` to use RAGAS metrics."
            ) from exc

        self._llm = _get_llm_wrapper(
            self.settings.judge_model,
            self.settings.openrouter_base_url,
            self.settings.openrouter_api_key,
            self.settings.judge_temperature,
        )
        self._embeddings = _get_embeddings(self.settings.ragas_embedding_model)

        self._metrics = {
            "faithfulness": Faithfulness(llm=self._llm),
            "answer_relevancy": AnswerRelevancy(llm=self._llm, embeddings=self._embeddings),
            "context_precision": ContextPrecision(llm=self._llm),
            "context_recall": ContextRecall(llm=self._llm),
        }

    async def _ascore_one(
        self,
        metric_name: str,
        sample: Any,
    ) -> float | None:
        metric = self._metrics[metric_name]
        try:
            score = await metric.single_turn_ascore(sample)
            return float(score) if score is not None else None
        except Exception as exc:
            logger.warning("RAGAS %s failed: %s", metric_name, exc)
            return None

    def evaluate(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        gold: list[str] | None = None,
        metrics: list[str] | None = None,
    ) -> RagasScores:
        try:
            self._ensure_loaded()
        except RuntimeError as exc:
            return RagasScores(error=str(exc))

        from ragas.dataset_schema import SingleTurnSample

        if metrics is None:
            metrics = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]

        # context_precision / context_recall need a reference (gold answer)
        reference = gold[0] if gold else None
        active = list(metrics)
        if reference is None:
            active = [m for m in active if m not in ("context_precision", "context_recall")]

        # Faithfulness and the context_* metrics need at least one context.
        if not contexts:
            active = [m for m in active if m not in ("faithfulness", "context_precision", "context_recall")]

        if not active:
            return RagasScores()

        sample = SingleTurnSample(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts or [""],
            reference=reference,
        )

        async def _run() -> dict[str, float | None]:
            tasks = {name: self._ascore_one(name, sample) for name in active}
            results: dict[str, float | None] = {}
            for name, coro in tasks.items():
                results[name] = await coro
            return results

        try:
            results = asyncio.run(_run())
        except RuntimeError:
            # Already inside an event loop (e.g. notebooks); fall back to a fresh loop.
            loop = asyncio.new_event_loop()
            try:
                results = loop.run_until_complete(_run())
            finally:
                loop.close()
        except Exception as exc:
            logger.exception("RAGAS evaluation failed")
            return RagasScores(error=str(exc))

        return RagasScores(
            faithfulness=results.get("faithfulness"),
            answer_relevancy=results.get("answer_relevancy"),
            context_precision=results.get("context_precision"),
            context_recall=results.get("context_recall"),
        )
