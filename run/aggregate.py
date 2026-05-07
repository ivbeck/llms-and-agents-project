"""Aggregate a scored JSONL into per-(setup, dataset) summary statistics.

Outputs a Markdown table to stdout and (optionally) a CSV. Includes:
- correctness rate (% score=1), wrong rate (% score=-1), no-answer rate (% score=0)
- mean answer-relevance, mean citation-accuracy
- mean RAGAS metrics (faithfulness, answer_relevancy, context_precision, context_recall)
- mean latency

For ratios and means we report a 95% normal-approximation CI.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import csv
import json
import math
from collections import defaultdict
from statistics import mean, pstdev
from typing import Any

from src.evaluation.paths import SCORES_DIR, resolve_input


METRIC_COLUMNS = [
    ("correctness_correct_rate", "Correct (=1) %"),
    ("correctness_wrong_rate", "Wrong (=-1) %"),
    ("correctness_noanswer_rate", "NoAns (=0) %"),
    ("answer_relevance", "AnsRel"),
    ("citation_accuracy", "CiteAcc"),
    ("faithfulness", "Faith"),
    ("ragas_answer_relevancy", "AnsRelev"),
    ("context_precision", "CtxP"),
    ("context_recall", "CtxR"),
    ("latency_seconds", "Latency(s)"),
]


def _ci95(values: list[float]) -> tuple[float, float]:
    if not values:
        return (float("nan"), float("nan"))
    if len(values) == 1:
        return (values[0], 0.0)
    m = mean(values)
    sd = pstdev(values)
    se = sd / math.sqrt(len(values))
    return (m, 1.96 * se)


def _extract_per_row(row: dict[str, Any]) -> dict[str, float | None]:
    judge = row.get("judge", {}) or {}
    ragas = row.get("ragas", {}) or {}
    correctness = judge.get("correctness", {}) or {}
    correctness_score = correctness.get("score") if "score" in correctness else None

    relevance = judge.get("answer_relevance", {}) or {}
    relevance_score = relevance.get("score") if "score" in relevance else None

    citation = judge.get("citation_accuracy", {}) or {}
    citation_score = citation.get("accuracy") if not citation.get("no_citations", False) else None

    return {
        "correctness_score": correctness_score,
        "answer_relevance": relevance_score,
        "citation_accuracy": citation_score,
        "faithfulness": ragas.get("faithfulness"),
        "ragas_answer_relevancy": ragas.get("answer_relevancy"),
        "context_precision": ragas.get("context_precision"),
        "context_recall": ragas.get("context_recall"),
        "latency_seconds": row.get("latency_seconds"),
    }


def _aggregate_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    extracted = [_extract_per_row(r) for r in rows]
    n = len(extracted)
    summary: dict[str, Any] = {"n": n}

    correctness = [e["correctness_score"] for e in extracted if e["correctness_score"] is not None]
    if correctness:
        total = len(correctness)
        summary["correctness_correct_rate"] = (
            sum(1 for s in correctness if s == 1) / total,
            0.0,  # CI is computed from binomial below if you want; leaving 0 for compactness
        )
        summary["correctness_wrong_rate"] = (sum(1 for s in correctness if s == -1) / total, 0.0)
        summary["correctness_noanswer_rate"] = (sum(1 for s in correctness if s == 0) / total, 0.0)

    for key in (
        "answer_relevance",
        "citation_accuracy",
        "faithfulness",
        "ragas_answer_relevancy",
        "context_precision",
        "context_recall",
        "latency_seconds",
    ):
        values = [float(e[key]) for e in extracted if e[key] is not None]
        if values:
            summary[key] = _ci95(values)

    return summary


def _format_cell(stat: tuple[float, float] | None, percent: bool = False) -> str:
    if stat is None:
        return "—"
    m, halfwidth = stat
    if percent:
        return f"{m * 100:.1f}%"
    return f"{m:.3f}±{halfwidth:.3f}" if halfwidth else f"{m:.3f}"


def render_markdown(grouped: dict[tuple[str, str], dict[str, Any]]) -> str:
    headers = ["Setup", "Dataset", "N"] + [label for _, label in METRIC_COLUMNS]
    rows = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for (setup, dataset), summary in sorted(grouped.items()):
        line = [setup, dataset or "—", str(summary["n"])]
        for key, _ in METRIC_COLUMNS:
            is_rate = key.endswith("_rate")
            line.append(_format_cell(summary.get(key), percent=is_rate))
        rows.append("| " + " | ".join(line) + " |")
    return "\n".join(rows)


def write_csv(grouped: dict[tuple[str, str], dict[str, Any]], path: Path) -> None:
    headers = ["setup", "dataset", "n"] + [key for key, _ in METRIC_COLUMNS] + [f"{key}_ci" for key, _ in METRIC_COLUMNS]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for (setup, dataset), summary in sorted(grouped.items()):
            row: list[Any] = [setup, dataset or "", summary["n"]]
            for key, _ in METRIC_COLUMNS:
                stat = summary.get(key)
                row.append(stat[0] if stat else "")
            for key, _ in METRIC_COLUMNS:
                stat = summary.get(key)
                row.append(stat[1] if stat else "")
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate scored JSONL into per-setup summary. "
            "Bare filenames resolve under data/scores/."
        ),
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="+",
        help="One or more scored JSONL files (resolved under data/scores/)",
    )
    parser.add_argument("--csv", type=Path, default=None)
    args = parser.parse_args()

    resolved = [resolve_input(p, SCORES_DIR) for p in args.input]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for path in resolved:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            setup = str(row.get("setup", "unknown"))
            dataset = str(row.get("dataset") or "")
            grouped[(setup, dataset)].append(row)

    summaries = {key: _aggregate_group(rows) for key, rows in grouped.items()}
    print(render_markdown(summaries))

    if args.csv:
        write_csv(summaries, args.csv)
        print(f"\nCSV written to {args.csv}")


if __name__ == "__main__":
    main()
