#!/usr/bin/env python3
"""
Create a horizontally scrollable Markdown report from Q&A JSONL result files.

Usage:
    python jsonl_judges_to_md.py results/*.jsonl -o judges_report.md

With generated answers included:
    python jsonl_judges_to_md.py results/*.jsonl -o judges_report.md --include-answer

Use a different correctness field:
    python jsonl_judges_to_md.py results/*.jsonl \
        -o judges_report.md \
        --correctness-path judge.correctness.score

Each JSONL file becomes one judge-response column.
Rows are aligned by question_id.
Each column header shows the overall correctness percentage.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path, id_field: str) -> dict[str, dict[str, Any]]:
    """Read a JSONL file and return records indexed by question_id."""
    records: dict[str, dict[str, Any]] = {}

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {path} at line {line_no}: {e}") from e

            qid = str(obj.get(id_field) or f"{path.stem}_line_{line_no}")

            original_qid = qid
            duplicate_idx = 2
            while qid in records:
                qid = f"{original_qid}__dup{duplicate_idx}"
                duplicate_idx += 1

            records[qid] = obj

    return records


def esc(value: Any) -> str:
    """HTML-escape a value for safe insertion into the Markdown/HTML report."""
    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, indent=2)

    return html.escape(str(value))


def short_text(value: Any, max_chars: int = 1200) -> str:
    text = "" if value is None else str(value)

    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "..."

    return text


def format_score(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, float):
        return f"{value:.3f}"

    return str(value)


def get_nested(obj: dict[str, Any], path: str) -> Any:
    """
    Read a nested value using a dotted path.

    Example:
        get_nested(record, "judge.correctness.score")
    """
    current: Any = obj

    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)

    return current


def extract_correctness_value(record: dict[str, Any], correctness_path: str) -> float | None:
    """
    Extract one numeric correctness value from a record.

    Default expected path:
        judge.correctness.score

    Usually:
        1 = correct
        0 = incorrect
    """
    value = get_nested(record, correctness_path)

    if value is None:
        return None

    if isinstance(value, bool):
        return 1.0 if value else 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def summarize_correctness(
    records: dict[str, dict[str, Any]],
    correctness_path: str,
    correctness_threshold: float,
) -> tuple[int, int, float | None]:
    """
    Return:
        correct_count, scored_count, percentage

    percentage is in the range 0-100.
    """
    correct_count = 0
    scored_count = 0

    for record in records.values():
        value = extract_correctness_value(record, correctness_path)

        if value is None:
            continue

        scored_count += 1

        if value >= correctness_threshold:
            correct_count += 1

    if scored_count == 0:
        return 0, 0, None

    return correct_count, scored_count, (correct_count / scored_count) * 100


def format_correctness_summary(
    records: dict[str, dict[str, Any]],
    correctness_path: str,
    correctness_threshold: float,
) -> str:
    correct_count, scored_count, percentage = summarize_correctness(
        records=records,
        correctness_path=correctness_path,
        correctness_threshold=correctness_threshold,
    )

    if percentage is None:
        return '<span class="muted">No correctness score found</span>'

    return (
        f'<span class="accuracy">{percentage:.1f}% correct</span><br>'
        f'<span class="muted">{correct_count} / {scored_count}</span>'
    )


def format_judge(judge: Any) -> str:
    """
    Convert a nested judge object into readable HTML.

    Expected structure can be like:
    {
      "correctness": {"rationale": "...", "score": 1},
      "answer_relevance": {"rationale": "...", "score": 1},
      "citation_accuracy": {
        "checks": [...],
        "accuracy": 1.0,
        "no_citations": false
      }
    }
    """
    if judge is None:
        return '<em class="muted">No judge field found</em>'

    if isinstance(judge, str):
        return f"<pre>{esc(judge)}</pre>"

    if not isinstance(judge, dict):
        return f"<pre>{esc(judge)}</pre>"

    blocks: list[str] = []

    for section_name, section_value in judge.items():
        section_title = esc(section_name)

        if isinstance(section_value, dict):
            summary_bits: list[str] = []

            if "score" in section_value:
                summary_bits.append(
                    f"score: {esc(format_score(section_value.get('score')))}"
                )

            if "accuracy" in section_value:
                summary_bits.append(
                    f"accuracy: {esc(format_score(section_value.get('accuracy')))}"
                )

            if "no_citations" in section_value:
                summary_bits.append(
                    f"no_citations: {esc(section_value.get('no_citations'))}"
                )

            summary = ""
            if summary_bits:
                summary = " — " + ", ".join(summary_bits)

            body_parts: list[str] = []

            rationale = section_value.get("rationale")
            if rationale:
                body_parts.append(
                    f"<p><strong>Rationale:</strong> {esc(rationale)}</p>"
                )

            checks = section_value.get("checks")
            if isinstance(checks, list):
                check_items: list[str] = []

                for check in checks:
                    if isinstance(check, dict):
                        evidence_id = esc(check.get("evidence_id", ""))
                        claim = esc(check.get("claim", ""))
                        supported = esc(check.get("supported", ""))
                        check_rationale = esc(check.get("rationale", ""))

                        check_items.append(
                            "<li>"
                            f"<strong>{evidence_id}</strong> "
                            f"supported=<code>{supported}</code><br>"
                            f"<strong>Claim:</strong> {claim}<br>"
                            f"<strong>Rationale:</strong> {check_rationale}"
                            "</li>"
                        )
                    else:
                        check_items.append(f"<li>{esc(check)}</li>")

                body_parts.append("<ul>" + "\n".join(check_items) + "</ul>")

            handled = {"score", "accuracy", "no_citations", "rationale", "checks"}
            remaining = {
                k: v
                for k, v in section_value.items()
                if k not in handled
            }

            if remaining:
                body_parts.append(f"<pre>{esc(remaining)}</pre>")

            blocks.append(
                "<details open>"
                f"<summary>{section_title}{summary}</summary>"
                f"{''.join(body_parts)}"
                "</details>"
            )

        else:
            blocks.append(
                "<details open>"
                f"<summary>{section_title}</summary>"
                f"<pre>{esc(section_value)}</pre>"
                "</details>"
            )

    return "\n".join(blocks)


def get_first_available(
    qid: str,
    file_records: dict[Path, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    """Return the first record found for a question ID across all files."""
    for records in file_records.values():
        if qid in records:
            return records[qid]

    return {}


def build_markdown(
    file_records: dict[Path, dict[str, dict[str, Any]]],
    judge_field: str,
    include_answer: bool,
    correctness_path: str,
    correctness_threshold: float,
) -> str:
    """Build the final Markdown report."""
    all_qids = sorted({
        qid
        for records in file_records.values()
        for qid in records.keys()
    })

    num_judge_cols = len(file_records)
    table_min_width = 900 + (num_judge_cols * 520)

    lines: list[str] = []

    lines.append("# Q&A Judge Report\n")
    lines.append(
        "This report is horizontally scrollable. "
        "Each result file is shown as one judge-response column. "
        "Each judge column header shows the overall correctness percentage.\n"
    )

    lines.append("<style>")
    lines.append(f"""
.qa-scroll-container {{
  width: 100%;
  overflow-x: auto;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  padding: 12px;
}}

.qa-table {{
  border-collapse: collapse;
  min-width: {table_min_width}px;
  font-size: 14px;
}}

.qa-table th,
.qa-table td {{
  border: 1px solid #d0d7de;
  padding: 8px;
  vertical-align: top;
}}

.qa-table th {{
  background: #f6f8fa;
  position: sticky;
  top: 0;
  z-index: 1;
}}

.qa-table .qid {{
  min-width: 180px;
  max-width: 240px;
}}

.qa-table .dataset {{
  min-width: 120px;
}}

.qa-table .gold {{
  min-width: 160px;
  max-width: 240px;
}}

.qa-table .question {{
  min-width: 360px;
  max-width: 520px;
}}

.qa-table .answer {{
  min-width: 420px;
  max-width: 560px;
}}

.qa-table .judge {{
  min-width: 480px;
  max-width: 600px;
}}

.qa-cell {{
  max-height: 420px;
  overflow-y: auto;
  white-space: normal;
}}

.qa-cell pre {{
  white-space: pre-wrap;
  word-break: break-word;
  margin: 6px 0;
  font-size: 12px;
}}

.qa-cell details {{
  margin-bottom: 8px;
}}

.qa-cell summary {{
  cursor: pointer;
  font-weight: 600;
}}

.file-name {{
  font-weight: 700;
}}

.accuracy {{
  font-weight: 700;
  font-size: 15px;
}}

.muted {{
  color: #57606a;
  font-size: 12px;
}}
""")
    lines.append("</style>\n")

    lines.append("## Files\n")

    for path, records in file_records.items():
        correct_count, scored_count, percentage = summarize_correctness(
            records=records,
            correctness_path=correctness_path,
            correctness_threshold=correctness_threshold,
        )

        if percentage is None:
            correctness_text = "correctness: not found"
        else:
            correctness_text = f"{percentage:.1f}% correct ({correct_count} / {scored_count})"

        lines.append(f"- `{esc(path.name)}`: {len(records)} records, {correctness_text}")

    lines.append("")

    lines.append('<div class="qa-scroll-container">')
    lines.append('<table class="qa-table">')

    header_cells = [
        '<th class="qid">question_id</th>',
        '<th class="dataset">dataset</th>',
        '<th class="gold">gold</th>',
        '<th class="question">question</th>',
    ]

    if include_answer:
        header_cells.append('<th class="answer">answer</th>')

    for path, records in file_records.items():
        correctness_summary = format_correctness_summary(
            records=records,
            correctness_path=correctness_path,
            correctness_threshold=correctness_threshold,
        )

        header_cells.append(
            '<th class="judge">'
            f'<span class="file-name">{esc(path.name)}</span><br>'
            f'{correctness_summary}'
            '</th>'
        )

    lines.append("<thead>")
    lines.append("<tr>" + "".join(header_cells) + "</tr>")
    lines.append("</thead>")

    lines.append("<tbody>")

    for qid in all_qids:
        base = get_first_available(qid, file_records)

        row_cells = [
            f'<td class="qid"><div class="qa-cell"><code>{esc(qid)}</code></div></td>',
            f'<td class="dataset"><div class="qa-cell">{esc(base.get("dataset", ""))}</div></td>',
            f'<td class="gold"><div class="qa-cell"><pre>{esc(base.get("gold", ""))}</pre></div></td>',
            f'<td class="question"><div class="qa-cell">{esc(base.get("question", ""))}</div></td>',
        ]

        if include_answer:
            row_cells.append(
                f'<td class="answer"><div class="qa-cell">'
                f'{esc(short_text(base.get("answer", ""), 1200))}'
                f'</div></td>'
            )

        for path, records in file_records.items():
            record = records.get(qid)

            if record is None:
                cell_html = '<em class="muted">Missing in this file</em>'
            else:
                judge = record.get(judge_field)

                # Fallback for schemas that use "critic" instead of "judge".
                if judge is None and judge_field == "judge":
                    judge = record.get("critic")

                setup = record.get("setup")
                latency = record.get("latency_seconds")
                correctness_value = extract_correctness_value(record, correctness_path)

                meta: list[str] = []

                if correctness_value is not None:
                    meta.append(
                        f"<p><strong>correctness:</strong> "
                        f"<code>{esc(format_score(correctness_value))}</code></p>"
                    )

                if setup:
                    meta.append(
                        f"<p><strong>setup:</strong> <code>{esc(setup)}</code></p>"
                    )

                if latency is not None:
                    meta.append(
                        f"<p><strong>latency:</strong> {esc(format_score(latency))}s</p>"
                    )

                cell_html = "".join(meta) + format_judge(judge)

            row_cells.append(
                f'<td class="judge"><div class="qa-cell">{cell_html}</div></td>'
            )

        lines.append("<tr>" + "".join(row_cells) + "</tr>")

    lines.append("</tbody>")
    lines.append("</table>")
    lines.append("</div>")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a horizontally scrollable Markdown judge report from JSONL files."
    )

    parser.add_argument(
        "jsonl_files",
        nargs="+",
        type=Path,
        help="Input .jsonl files. Each file becomes one judge column.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("judges_report.md"),
        help="Output Markdown file.",
    )

    parser.add_argument(
        "--id-field",
        default="question_id",
        help="Field used to align rows across files. Default: question_id",
    )

    parser.add_argument(
        "--judge-field",
        default="judge",
        help="Field containing judge responses. Default: judge",
    )

    parser.add_argument(
        "--correctness-path",
        default="judge.correctness.score",
        help=(
            "Dotted path used to compute the correctness percentage. "
            "Default: judge.correctness.score"
        ),
    )

    parser.add_argument(
        "--correctness-threshold",
        type=float,
        default=1.0,
        help=(
            "Minimum correctness value required to count as correct. "
            "Default: 1.0"
        ),
    )

    parser.add_argument(
        "--include-answer",
        action="store_true",
        help="Also include the generated answer as a metadata column.",
    )

    args = parser.parse_args()

    file_records: dict[Path, dict[str, dict[str, Any]]] = {}

    for path in args.jsonl_files:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix != ".jsonl":
            print(f"Warning: {path} does not end with .jsonl")

        file_records[path] = read_jsonl(path, args.id_field)

    markdown = build_markdown(
        file_records=file_records,
        judge_field=args.judge_field,
        include_answer=args.include_answer,
        correctness_path=args.correctness_path,
        correctness_threshold=args.correctness_threshold,
    )

    args.output.write_text(markdown, encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()