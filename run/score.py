"""Score predictions JSONL with LLM-as-judge and RAGAS metrics.

Example:
    python score.py predictions.jsonl --output scored.jsonl
    python score.py predictions.jsonl --metrics correctness,faithfulness
    python score.py predictions.jsonl --judge-model anthropic/claude-haiku-4-5
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import logging

from src.config import Settings
from src.evaluation.paths import PREDICTIONS_DIR, SCORES_DIR, derive_output, resolve_input
from src.evaluation.runner import ALL_METRICS, ScoringRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Score a predictions JSONL file. Bare filenames resolve under "
            "data/predictions/; default output goes to data/scores/."
        ),
    )
    parser.add_argument("input", type=Path, help="JSONL output of eval.py (resolved under data/predictions/)")
    parser.add_argument("--output", type=Path, default=None, help="Default: data/scores/<stem>.jsonl")
    parser.add_argument(
        "--metrics",
        type=str,
        default=",".join(ALL_METRICS),
        help=f"Comma-separated metrics to compute. Available: {','.join(ALL_METRICS)}",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--judge-model", type=str, default=None, help="Override JUDGE_MODEL env")
    parser.add_argument("--log-level", default="INFO")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    args.input = resolve_input(args.input, PREDICTIONS_DIR)
    if args.output is None:
        args.output = derive_output(args.input, SCORES_DIR)

    settings = Settings()
    if args.judge_model:
        settings.judge_model = args.judge_model

    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    print(
        f"input:   {args.input}\n"
        f"output:  {args.output}\n"
        f"judge:   {settings.judge_model} (temperature={settings.judge_temperature})\n"
        f"metrics: {','.join(metrics)}"
    )

    runner = ScoringRunner(settings, metrics)
    runner.run(args.input, args.output, limit=args.limit)


if __name__ == "__main__":
    main()
