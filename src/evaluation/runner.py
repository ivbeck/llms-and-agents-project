"""Score a predictions JSONL file with LLM-as-judge and RAGAS metrics.

Reads a JSONL produced by eval.py (one row per question with answer +
evidence + optional gold) and writes a scored JSONL with the same rows
augmented by `judge` and `ragas` blocks.

Caching: rows already containing all requested metrics are passed through
unchanged. This lets you re-run scoring with new metrics without redoing
finished work, and resume after a crash.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from tqdm import tqdm

from src.config import Settings
from src.evaluation.judge import (
    AnswerRelevanceJudge,
    CitationAccuracyJudge,
    CorrectnessJudge,
    build_judge_llm,
)
from src.evaluation.ragas_metrics import RagasEvaluator

logger = logging.getLogger(__name__)


ALL_METRICS = (
    "correctness",
    "answer_relevance",
    "citation_accuracy",
    "faithfulness",
    "ragas_answer_relevancy",
    "context_precision",
    "context_recall",
)

_RAGAS_METRICS = {
    "faithfulness": "faithfulness",
    "ragas_answer_relevancy": "answer_relevancy",
    "context_precision": "context_precision",
    "context_recall": "context_recall",
}


def _row_has_metric(row: dict[str, Any], metric: str) -> bool:
    if metric == "correctness":
        return "correctness" in row.get("judge", {})
    if metric == "answer_relevance":
        return "answer_relevance" in row.get("judge", {})
    if metric == "citation_accuracy":
        return "citation_accuracy" in row.get("judge", {})
    if metric in _RAGAS_METRICS:
        ragas = row.get("ragas", {})
        return ragas.get(_RAGAS_METRICS[metric]) is not None
    return False


def _missing_metrics(row: dict[str, Any], requested: list[str]) -> list[str]:
    return [m for m in requested if not _row_has_metric(row, m)]


class ScoringRunner:
    def __init__(self, settings: Settings, metrics: list[str]) -> None:
        self.settings = settings
        self.metrics = metrics
        unknown = [m for m in metrics if m not in ALL_METRICS]
        if unknown:
            raise ValueError(f"Unknown metrics requested: {unknown}. Known: {ALL_METRICS}")

        self._judge_llm = None
        self._correctness: CorrectnessJudge | None = None
        self._relevance: AnswerRelevanceJudge | None = None
        self._citation: CitationAccuracyJudge | None = None
        self._ragas: RagasEvaluator | None = None

    def _ensure_judges(self) -> None:
        if self._judge_llm is not None:
            return
        self._judge_llm = build_judge_llm(self.settings)
        if "correctness" in self.metrics:
            self._correctness = CorrectnessJudge(self._judge_llm)
        if "answer_relevance" in self.metrics:
            self._relevance = AnswerRelevanceJudge(self._judge_llm)
        if "citation_accuracy" in self.metrics:
            self._citation = CitationAccuracyJudge(self._judge_llm)

    def _ensure_ragas(self) -> None:
        if self._ragas is not None:
            return
        if any(m in _RAGAS_METRICS for m in self.metrics):
            self._ragas = RagasEvaluator(self.settings)

    def score_row(self, row: dict[str, Any]) -> dict[str, Any]:
        if "answer" not in row or row.get("error"):
            logger.info("Skipping row %s (error or no answer)", row.get("question_id"))
            return row

        missing = _missing_metrics(row, self.metrics)
        if not missing:
            return row

        question = row.get("question", "")
        answer = row.get("answer", "")
        gold: list[str] = list(row.get("gold") or [])
        evidence = row.get("evidence") or []
        contexts = [str(ev.get("text") or "") for ev in evidence if ev.get("text")]

        judge_block = dict(row.get("judge", {}))
        ragas_block = dict(row.get("ragas", {}))

        if any(m in missing for m in ("correctness", "answer_relevance", "citation_accuracy")):
            self._ensure_judges()

        if "correctness" in missing and self._correctness is not None:
            verdict = self._correctness.judge(question, answer, gold)
            judge_block["correctness"] = verdict.model_dump()

        if "answer_relevance" in missing and self._relevance is not None:
            verdict = self._relevance.judge(question, answer)
            judge_block["answer_relevance"] = verdict.model_dump()

        if "citation_accuracy" in missing and self._citation is not None:
            verdict = self._citation.judge(question, answer, evidence)
            judge_block["citation_accuracy"] = verdict.model_dump()

        ragas_missing = [m for m in missing if m in _RAGAS_METRICS]
        if ragas_missing:
            self._ensure_ragas()
            assert self._ragas is not None
            ragas_request = [_RAGAS_METRICS[m] for m in ragas_missing]
            scores = self._ragas.evaluate(
                question=question,
                answer=answer,
                contexts=contexts,
                gold=gold,
                metrics=ragas_request,
            )
            scored = scores.to_dict()
            for ragas_key in ragas_request:
                if ragas_block.get(ragas_key) is None:
                    ragas_block[ragas_key] = scored.get(ragas_key)
            if scored.get("error") and ragas_block.get("error") is None:
                ragas_block["error"] = scored["error"]

        if judge_block:
            row["judge"] = judge_block
        if ragas_block:
            row["ragas"] = ragas_block
        return row

    def run(
        self,
        input_path: Path,
        output_path: Path,
        limit: int | None = None,
    ) -> None:
        rows: list[dict[str, Any]] = []
        for line in input_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break

        logger.info("Scoring %d rows with metrics: %s", len(rows), self.metrics)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        correct_counts = {1: 0, 0: 0, -1: 0}
        skipped = 0
        total_elapsed = 0.0

        with output_path.open("w", encoding="utf-8") as handle:
            pbar = tqdm(rows, desc="scoring", unit="row")
            for row in pbar:
                started = time.perf_counter()
                scored = self.score_row(row)
                elapsed = round(time.perf_counter() - started, 3)
                scored.setdefault("scoring", {})["elapsed_seconds"] = elapsed
                handle.write(json.dumps(scored, ensure_ascii=False) + "\n")
                handle.flush()

                total_elapsed += elapsed
                correctness_score = (
                    scored.get("judge", {}).get("correctness", {}).get("score")
                    if isinstance(scored.get("judge"), dict)
                    else None
                )
                if correctness_score in correct_counts:
                    correct_counts[correctness_score] += 1
                elif scored.get("error") or "answer" not in scored:
                    skipped += 1

                done = sum(correct_counts.values()) + skipped
                postfix: dict[str, Any] = {
                    "qid": str(row.get("question_id"))[:14],
                    "t": f"{elapsed:.1f}s",
                }
                if "correctness" in self.metrics and done:
                    postfix["+1"] = correct_counts[1]
                    postfix["0"] = correct_counts[0]
                    postfix["-1"] = correct_counts[-1]
                if skipped:
                    postfix["skip"] = skipped
                pbar.set_postfix(postfix)

        summary_parts = [f"Scored {len(rows)} rows -> {output_path}", f"total={total_elapsed:.1f}s"]
        if "correctness" in self.metrics:
            graded = sum(correct_counts.values())
            if graded:
                summary_parts.append(
                    f"correct={correct_counts[1]}/{graded} ({correct_counts[1] / graded * 100:.1f}%)"
                )
        if skipped:
            summary_parts.append(f"skipped={skipped}")
        print(" | ".join(summary_parts))
