"""Batch evaluation runner for RAG setup comparisons."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run RAG ablation evaluations over questions.")
    parser.add_argument("input", type=Path, help="JSONL or plain-text file with questions")
    parser.add_argument("--output", type=Path, default=Path("eval_results.jsonl"))
    parser.add_argument("--setup", choices=["baseline", "full"], default="full")
    parser.add_argument("--limit", type=int, default=None)
    return parser


def load_questions(path: Path, limit: int | None = None) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            data: Any = json.loads(line)
            if isinstance(data, dict):
                question = str(data.get("question", "")).strip()
                question_id = str(data.get("id", line_number))
            else:
                question = str(data).strip()
                question_id = str(line_number)
        except json.JSONDecodeError:
            question = line
            question_id = str(line_number)

        if question:
            questions.append({"id": question_id, "question": question})
        if limit is not None and len(questions) >= limit:
            break
    return questions


def configure_setup(settings: Any, setup: str) -> Any:
    if setup == "baseline":
        settings.enable_hybrid_retrieval = False
        settings.enable_cross_encoder_reranking = False
        settings.enable_query_decomposition = False
        settings.enable_iterative_retrieval = False
        settings.enable_self_rag = False
        settings.enable_evidence_filtering = False
        settings.enable_evidence_sufficiency = False
        settings.enable_hyde = False
    return settings


def main() -> None:
    args = build_parser().parse_args()
    from src.config import Settings
    from src.orchestrator import AdvancedMultiAgentRAGSystem

    settings = configure_setup(Settings(), args.setup)
    system = AdvancedMultiAgentRAGSystem(settings)
    questions = load_questions(args.input, args.limit)

    with args.output.open("w", encoding="utf-8") as handle:
        for item in questions:
            started = time.perf_counter()
            row: dict[str, Any] = {
                "question_id": item["id"],
                "question": item["question"],
                "setup": args.setup,
            }
            try:
                result = system.answer_question(item["question"])
                row.update(
                    {
                        "latency_seconds": round(time.perf_counter() - started, 3),
                        "answer": result.answer,
                        "critic": result.critic.model_dump(),
                        "features": result.features.model_dump(),
                        "sources_count": len(result.sources),
                        "evidence_count": len(result.evidence),
                        "evidence": [
                            {
                                "evidence_id": ev.evidence_id,
                                "url": ev.url,
                                "title": ev.title,
                                "score_final": ev.score_final,
                                "selected_reason": ev.selected_reason,
                            }
                            for ev in result.evidence
                        ],
                    }
                )
            except Exception as exc:
                row.update(
                    {
                        "latency_seconds": round(time.perf_counter() - started, 3),
                        "error": str(exc),
                    }
                )

            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
