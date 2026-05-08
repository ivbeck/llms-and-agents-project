"""Batch evaluation runner for RAG setup comparisons.

Produces a predictions JSONL: one row per question with the system's answer,
evidence, latency, and any gold/dataset metadata copied from the input.
Scoring (LLM-as-judge, RAGAS) is a separate stage; see score.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
import time
from typing import Any

from tqdm import tqdm

STEP_OPTIONS: list[tuple[str, str, str]] = [
    ("enable_hybrid_retrieval", "Hybrid retrieval", "hybrid"),
    ("enable_cross_encoder_reranking", "Cross-encoder reranking", "rerank"),
    ("enable_query_decomposition", "Query decomposition", "decompose"),
    ("enable_iterative_retrieval", "Iterative retrieval", "iterative"),
    ("enable_self_rag", "Self-RAG", "self-rag"),
    ("enable_evidence_filtering", "Evidence filtering", "filter"),
    ("enable_evidence_sufficiency", "Evidence sufficiency checks", "sufficiency"),
    ("enable_hyde", "HyDE", "hyde"),
]

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run RAG ablation evaluations over questions. "
            "Bare filenames resolve under data/benchmarks/; "
            "default output goes to data/predictions/."
        ),
    )
    parser.add_argument("input", type=Path, help="JSONL question file (resolved under data/benchmarks/)")
    parser.add_argument("--output", type=Path, default=None, help="Default: data/predictions/<stem>_<setup>.jsonl")
    parser.add_argument("--setup", choices=["baseline", "full"], default="full")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--no-interactive-steps",
        action="store_true",
        help="Skip interactive step selection and use --setup only.",
    )
    return parser


def _normalize_gold(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def load_questions(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            data: Any = json.loads(line)
            if isinstance(data, dict):
                question = str(data.get("question", "")).strip()
                question_id = str(data.get("id", line_number))
                gold = _normalize_gold(data.get("gold") or data.get("answer") or data.get("answers"))
                dataset = str(data.get("dataset", "")).strip() or None
            else:
                question = str(data).strip()
                question_id = str(line_number)
                gold = []
                dataset = None
        except json.JSONDecodeError:
            question = line
            question_id = str(line_number)
            gold = []
            dataset = None

        if question:
            questions.append({
                "id": question_id,
                "question": question,
                "gold": gold,
                "dataset": dataset,
            })
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


def _render_step_options(enabled: dict[str, bool]) -> str:
    lines = []
    for index, (attr, label, key) in enumerate(STEP_OPTIONS, start=1):
        marker = "x" if enabled.get(attr, True) else " "
        lines.append(f"{index}. [{marker}] {label} ({key})")
    return "\n".join(lines)


def _interactive_step_selection(settings: Any, setup: str) -> tuple[Any, str]:
    enabled = {attr: bool(getattr(settings, attr, True)) for attr, _, _ in STEP_OPTIONS}

    if not sys.stdin.isatty():
        for attr, is_enabled in enabled.items():
            setattr(settings, attr, is_enabled)
        selected = [key for attr, _, key in STEP_OPTIONS if enabled[attr]]
        return settings, ("full" if len(selected) == len(STEP_OPTIONS) else ",".join(selected) or "none")

    while True:
        print("\nSelect enabled evaluation steps (all enabled by default):")
        print(_render_step_options(enabled))
        print("Toggle by number or key (comma-separated), Enter to continue, 'a' all, 'n' none.")
        raw = input("steps> ").strip().lower()
        if not raw:
            break
        if raw in {"a", "all"}:
            for attr in enabled:
                enabled[attr] = True
            continue
        if raw in {"n", "none"}:
            for attr in enabled:
                enabled[attr] = False
            continue

        tokens = [token.strip() for token in raw.split(",") if token.strip()]
        changed = False
        for token in tokens:
            if token.isdigit():
                idx = int(token)
                if 1 <= idx <= len(STEP_OPTIONS):
                    attr = STEP_OPTIONS[idx - 1][0]
                    enabled[attr] = not enabled[attr]
                    changed = True
                    continue

            for attr, _, key in STEP_OPTIONS:
                if token == key:
                    enabled[attr] = not enabled[attr]
                    changed = True
                    break

        if not changed:
            print("No valid step keys/numbers provided; try again.")

    for attr, is_enabled in enabled.items():
        setattr(settings, attr, is_enabled)

    selected = [key for attr, _, key in STEP_OPTIONS if enabled[attr]]
    if len(selected) == len(STEP_OPTIONS):
        setup_label = "full"
    elif not selected:
        setup_label = "none"
    else:
        setup_label = ",".join(selected)
    return settings, setup_label


def main() -> None:
    args = build_parser().parse_args()
    from src.config import Settings
    from src.evaluation.paths import BENCHMARKS_DIR, PREDICTIONS_DIR, derive_output, resolve_input
    from src.orchestrator import AdvancedMultiAgentRAGSystem

    args.input = resolve_input(args.input, BENCHMARKS_DIR)
    settings = configure_setup(Settings(), args.setup)
    setup_label = args.setup
    if not args.no_interactive_steps:
        settings, setup_label = _interactive_step_selection(settings, args.setup)

    if args.output is None:
        args.output = derive_output(args.input, PREDICTIONS_DIR, suffix=setup_label.replace(",", "_"))
    print(f"input:  {args.input}\noutput: {args.output}\nsetup:  {setup_label}")

    system = AdvancedMultiAgentRAGSystem(settings)
    questions = load_questions(args.input, args.limit)

    successes = 0
    errors = 0
    total_latency = 0.0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        pbar = tqdm(questions, desc=f"eval[{setup_label}]", unit="q")
        for item in pbar:
            started = time.perf_counter()
            row: dict[str, Any] = {
                "question_id": item["id"],
                "question": item["question"],
                "gold": item["gold"],
                "dataset": item["dataset"],
                "setup": setup_label,
            }
            try:
                result = system.answer_question(item["question"])
                latency = round(time.perf_counter() - started, 3)
                row.update(
                    {
                        "latency_seconds": latency,
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
                                "text": ev.text,
                                "score_final": ev.score_final,
                                "selected_reason": ev.selected_reason,
                            }
                            for ev in result.evidence
                        ],
                    }
                )
                successes += 1
            except Exception as exc:
                latency = round(time.perf_counter() - started, 3)
                row.update({"latency_seconds": latency, "error": str(exc)})
                errors += 1

            total_latency += latency
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()

            done = successes + errors
            pbar.set_postfix(
                ok=successes,
                err=errors,
                last=f"{latency:.1f}s",
                avg=f"{total_latency / done:.1f}s",
            )

    print(
        f"Wrote {successes + errors} rows to {args.output} "
        f"(ok={successes}, err={errors}, total={total_latency:.1f}s)"
    )


if __name__ == "__main__":
    main()
