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

import os
from pathlib import Path


def _discover_project_root() -> Path:
    """Resolve the checkout root that owns ``data/``.

    ``Path(__file__).parents[2]`` breaks when this package is installed under
    ``site-packages`` (that becomes the bogus "project root" and outputs land in
    ``site-packages/data/``). Prefer the cwd chain (when you run the CLI from the
    repo), then walk upward from ``paths.py``, then fall back to the old rule.
    """

    env = os.environ.get("LLMS_AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()

    here = Path(__file__).resolve()

    def looks_like_repo(root: Path) -> bool:
        if not (root / "pyproject.toml").is_file():
            return False
        if (root / "data").is_dir():
            return True
        return (root / "src" / "evaluation").is_dir()

    ordered: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        if path not in seen:
            seen.add(path)
            ordered.append(path)

    cwd = Path.cwd().resolve()
    add(cwd)
    for p in cwd.parents:
        add(p)
    for p in here.parents:
        add(p)

    for base in ordered:
        if looks_like_repo(base):
            return base

    return here.parents[2]


PROJECT_ROOT = _discover_project_root()
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
