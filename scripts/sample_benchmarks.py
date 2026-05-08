"""Randomly sample a mixed evaluation set from SimpleQA, TriviaQA, and PopQA.

Defaults: 30 SimpleQA + 10 TriviaQA + 10 PopQA = 50 questions, seeded.

Usage:
    python scripts/sample_benchmarks.py
    python scripts/sample_benchmarks.py --out data/benchmarks/mixed_50.jsonl --seed 7
    python scripts/sample_benchmarks.py --simpleqa 30 --triviaqa 10 --popqa 10
"""

from __future__ import annotations

import argparse
import json
import logging
import random
from pathlib import Path
from typing import Any, Callable

from download_benchmarks import (
    _write_jsonl,
    load_popqa,
    load_simpleqa,
    load_triviaqa,
)

logger = logging.getLogger(__name__)

LOADERS: dict[str, Callable[[], list[dict[str, Any]]]] = {
    "simpleqa": load_simpleqa,
    "triviaqa": load_triviaqa,
    "popqa": load_popqa,
}


def sample(rows: list[dict[str, Any]], n: int, rng: random.Random) -> list[dict[str, Any]]:
    if n >= len(rows):
        logger.warning("Requested %d rows but dataset only has %d; returning all.", n, len(rows))
        return list(rows)
    return rng.sample(rows, n)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sample a mixed eval set from QA benchmarks.")
    parser.add_argument("--simpleqa", type=int, default=30)
    parser.add_argument("--triviaqa", type=int, default=10)
    parser.add_argument("--popqa", type=int, default=10)
    parser.add_argument("--out", type=Path, default=Path("data/benchmarks/mixed_50.jsonl"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--shuffle", action="store_true", help="Shuffle the final combined set.")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    counts = {"simpleqa": args.simpleqa, "triviaqa": args.triviaqa, "popqa": args.popqa}
    rng = random.Random(args.seed)

    combined: list[dict[str, Any]] = []
    summary: list[str] = []
    for name, n in counts.items():
        if n <= 0:
            continue
        rows = LOADERS[name]()
        picked = sample(rows, n, rng)
        combined.extend(picked)
        summary.append(f"{name}: sampled {len(picked)} of {len(rows)}")

    if args.shuffle:
        rng.shuffle(combined)

    written = _write_jsonl(combined, args.out)
    summary.append(f"total: {written} rows -> {args.out}")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
