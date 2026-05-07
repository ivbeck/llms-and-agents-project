"""Shared path conventions for the evaluation pipeline.

Layout under the project root:

    data/
      benchmarks/   ← question files from scripts/download_benchmarks.py
      predictions/  ← outputs of run/eval.py
      scores/       ← outputs of run/score.py and run/aggregate.py

CLI scripts default to the right subdir for their stage and accept either a
plain filename (resolved against the convention) or an explicit absolute /
relative path.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
BENCHMARKS_DIR = DATA_DIR / "benchmarks"
PREDICTIONS_DIR = DATA_DIR / "predictions"
SCORES_DIR = DATA_DIR / "scores"


def resolve_input(path: Path, default_dir: Path) -> Path:
    """Resolve a user-provided input path.

    If `path` is absolute, exists as-is, or contains a directory component,
    return it untouched. Otherwise prepend `default_dir`. This lets users say
    `simpleqa.jsonl` and have it resolve under `data/benchmarks/`, while still
    accepting `./foo/bar.jsonl` or absolute paths verbatim.
    """
    if path.is_absolute() or path.exists() or len(path.parts) > 1:
        return path
    return default_dir / path


def derive_output(input_path: Path, default_dir: Path, suffix: str = "") -> Path:
    """Build a default output path inside `default_dir` based on the input stem."""
    stem = input_path.stem
    if suffix:
        stem = f"{stem}_{suffix}"
    return default_dir / f"{stem}.jsonl"
