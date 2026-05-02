"""Robust parsing helpers for LLM JSON outputs."""

from __future__ import annotations

import json
import re
from typing import Any


def _strip_json_fence(text: str) -> str:
    fenced = re.fullmatch(r"\s*```(?:json)?\s*(.*?)\s*```\s*", text, re.DOTALL)
    return fenced.group(1).strip() if fenced else text.strip()


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first valid JSON object from an LLM response."""
    text = _strip_json_fence(text)
    decoder = json.JSONDecoder()

    for match in re.finditer(r"\{", text):
        try:
            parsed, _ = decoder.raw_decode(text[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise ValueError(f"Could not extract JSON object from model output: {text}")
