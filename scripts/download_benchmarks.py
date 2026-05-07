"""Download benchmark datasets and normalize them to the JSONL format eval.py expects.

Output schema (one row per question):
    {"id": "...", "question": "...", "gold": ["..."], "dataset": "..."}

Usage:
    python scripts/download_benchmarks.py --out data/
    python scripts/download_benchmarks.py --datasets simpleqa,popqa --sample 100
    python scripts/download_benchmarks.py --datasets browsecomp --sample 50

Notes:
- TriviaQA + PopQA come from HuggingFace `datasets` (public, no auth needed).
- SimpleQA + BrowseComp come from OpenAI's simple-evals public blob storage.
- BrowseComp is XOR-encrypted with a per-row canary; we decrypt on download.
  If OpenAI changes the URL or scheme, grab the latest decryption logic from
  https://github.com/openai/simple-evals/blob/main/browsecomp_eval.py
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import logging
import random
from pathlib import Path
from typing import Any, Callable, Iterable

from tqdm import tqdm

logger = logging.getLogger(__name__)

SIMPLEQA_URL = "https://openaipublic.blob.core.windows.net/simple-evals/simple_qa_test_set.csv"
BROWSECOMP_URL = "https://openaipublic.blob.core.windows.net/simple-evals/browse_comp_test_set.csv"


def _write_jsonl(rows: Iterable[dict[str, Any]], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def _maybe_sample(rows: list[dict[str, Any]], sample: int | None, seed: int) -> list[dict[str, Any]]:
    if sample is None or sample >= len(rows):
        return rows
    rng = random.Random(seed)
    return rng.sample(rows, sample)


# ---------- SimpleQA ----------

def load_simpleqa() -> list[dict[str, Any]]:
    import requests

    logger.info("Downloading SimpleQA from %s", SIMPLEQA_URL)
    resp = requests.get(SIMPLEQA_URL, timeout=60)
    resp.raise_for_status()
    raw_rows = list(csv.DictReader(io.StringIO(resp.text)))
    rows: list[dict[str, Any]] = []
    for idx, raw in enumerate(tqdm(raw_rows, desc="simpleqa", unit="q")):
        question = (raw.get("problem") or raw.get("question") or "").strip()
        answer = (raw.get("answer") or "").strip()
        if not question or not answer:
            continue
        rows.append({
            "id": f"simpleqa_{idx}",
            "question": question,
            "gold": [answer],
            "dataset": "simpleqa",
        })
    logger.info("SimpleQA: %d rows", len(rows))
    return rows


# ---------- PopQA ----------

def load_popqa() -> list[dict[str, Any]]:
    from datasets import load_dataset

    logger.info("Loading PopQA from HuggingFace (akariasai/PopQA)")
    ds = load_dataset("akariasai/PopQA", split="test")
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(tqdm(ds, desc="popqa", unit="q", total=len(ds))):
        question = (item.get("question") or "").strip()
        possible_raw = item.get("possible_answers")
        if isinstance(possible_raw, str):
            try:
                possible = json.loads(possible_raw)
            except json.JSONDecodeError:
                possible = [possible_raw]
        elif isinstance(possible_raw, list):
            possible = possible_raw
        else:
            possible = []
        gold = [str(a).strip() for a in possible if str(a).strip()]
        if not question or not gold:
            continue
        rows.append({
            "id": f"popqa_{item.get('id', idx)}",
            "question": question,
            "gold": gold,
            "dataset": "popqa",
        })
    logger.info("PopQA: %d rows", len(rows))
    return rows


# ---------- TriviaQA ----------

def load_triviaqa(subset: str = "rc.nocontext") -> list[dict[str, Any]]:
    from datasets import load_dataset

    logger.info("Loading TriviaQA (%s) from HuggingFace", subset)
    # validation split has gold answers; test has none (held out)
    ds = load_dataset("trivia_qa", subset, split="validation")
    rows: list[dict[str, Any]] = []
    for item in tqdm(ds, desc="triviaqa", unit="q", total=len(ds)):
        question = (item.get("question") or "").strip()
        ans = item.get("answer") or {}
        value = (ans.get("value") or "").strip()
        aliases = [str(a).strip() for a in (ans.get("aliases") or []) if str(a).strip()]
        gold = [a for a in [value, *aliases] if a]
        # de-duplicate while preserving order
        seen: set[str] = set()
        gold = [a for a in gold if not (a.lower() in seen or seen.add(a.lower()))]
        qid = item.get("question_id") or item.get("id")
        if not question or not gold:
            continue
        rows.append({
            "id": f"triviaqa_{qid}",
            "question": question,
            "gold": gold,
            "dataset": "triviaqa",
        })
    logger.info("TriviaQA: %d rows", len(rows))
    return rows


# ---------- BrowseComp ----------

def _derive_key(password: str, length: int) -> bytes:
    """SHA-256 expanded key (matches OpenAI simple-evals)."""
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    repeats = length // len(digest) + 1
    return (digest * repeats)[:length]


def _decrypt(ciphertext_b64: str, password: str) -> str:
    encrypted = base64.b64decode(ciphertext_b64)
    key = _derive_key(password, len(encrypted))
    return bytes(a ^ b for a, b in zip(encrypted, key)).decode("utf-8")


def load_browsecomp() -> list[dict[str, Any]]:
    import requests

    logger.info("Downloading BrowseComp from %s", BROWSECOMP_URL)
    resp = requests.get(BROWSECOMP_URL, timeout=60)
    resp.raise_for_status()
    raw_rows = list(csv.DictReader(io.StringIO(resp.text)))
    rows: list[dict[str, Any]] = []
    for idx, raw in enumerate(tqdm(raw_rows, desc="browsecomp", unit="q")):
        canary = raw.get("canary") or ""
        problem_b64 = raw.get("problem") or ""
        answer_b64 = raw.get("answer") or ""
        if not canary or not problem_b64 or not answer_b64:
            continue
        try:
            question = _decrypt(problem_b64, canary).strip()
            answer = _decrypt(answer_b64, canary).strip()
        except Exception as exc:
            logger.warning("BrowseComp row %d failed to decrypt: %s", idx, exc)
            continue
        if not question or not answer:
            continue
        rows.append({
            "id": f"browsecomp_{idx}",
            "question": question,
            "gold": [answer],
            "dataset": "browsecomp",
        })
    logger.info("BrowseComp: %d rows decrypted", len(rows))
    return rows


# ---------- Driver ----------

LOADERS: dict[str, Callable[[], list[dict[str, Any]]]] = {
    "simpleqa": load_simpleqa,
    "popqa": load_popqa,
    "triviaqa": load_triviaqa,
    "browsecomp": load_browsecomp,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download QA benchmarks as eval-ready JSONL.")
    parser.add_argument(
        "--datasets",
        type=str,
        default=",".join(LOADERS.keys()),
        help=f"Comma-separated subset of: {','.join(LOADERS.keys())}",
    )
    parser.add_argument("--out", type=Path, default=Path("data/benchmarks"))
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="If set, randomly sample this many rows per dataset (seeded).",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    requested = [d.strip() for d in args.datasets.split(",") if d.strip()]
    unknown = [d for d in requested if d not in LOADERS]
    if unknown:
        raise SystemExit(f"Unknown datasets: {unknown}. Known: {list(LOADERS)}")

    args.out.mkdir(parents=True, exist_ok=True)

    summary: list[str] = []
    for name in tqdm(requested, desc="datasets", unit="ds", disable=len(requested) <= 1):
        try:
            rows = LOADERS[name]()
        except Exception as exc:
            logger.exception("Failed to load %s: %s", name, exc)
            summary.append(f"{name}: FAILED ({exc})")
            continue
        rows = _maybe_sample(rows, args.sample, args.seed)
        out_path = args.out / f"{name}.jsonl"
        n = _write_jsonl(rows, out_path)
        logger.info("Wrote %d rows to %s", n, out_path)
        summary.append(f"{name}: {n} rows -> {out_path}")

    print("\n".join(summary))


if __name__ == "__main__":
    main()
