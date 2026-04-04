"""General text helpers."""

from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def simple_tokens(text: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
    return [tok for tok in cleaned.split() if tok.strip()]
