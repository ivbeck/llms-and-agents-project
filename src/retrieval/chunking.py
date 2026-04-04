"""Text chunking utilities."""

from __future__ import annotations

from src.utils.text import normalize_whitespace


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    clean = normalize_whitespace(text)
    if not clean:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[str] = []
    start = 0
    step = chunk_size - overlap
    while start < len(clean):
        chunks.append(clean[start:start + chunk_size])
        start += step
    return chunks


def deduplicate_chunks(chunks: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for chunk in chunks:
        norm = chunk.strip()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        unique.append(norm)
    return unique
