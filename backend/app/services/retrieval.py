from __future__ import annotations

import re
from collections import Counter

from app.models.document import SearchResult
from app.services.document_store import load_all_chunks


def search(query: str, top_k: int = 5) -> list[SearchResult]:
    """Simple keyword-based retrieval over all document chunks.

    Uses TF-based scoring: counts how many query terms appear in each chunk.
    Good enough for a workshop demo without requiring embeddings or a vector DB.
    """
    chunks = load_all_chunks()
    if not chunks:
        return []

    query_terms = _tokenize(query)
    if not query_terms:
        return []

    scored: list[tuple[float, int]] = []
    for i, chunk in enumerate(chunks):
        chunk_tokens = _tokenize(chunk.text)
        if not chunk_tokens:
            continue

        chunk_counter = Counter(chunk_tokens)
        score = sum(chunk_counter.get(term, 0) for term in query_terms) / len(chunk_tokens)

        if score > 0:
            scored.append((score, i))

    scored.sort(key=lambda x: x[0], reverse=True)

    results: list[SearchResult] = []
    for score, idx in scored[:top_k]:
        chunk = chunks[idx]
        results.append(
            SearchResult(
                document_id=chunk.document_id,
                filename=chunk.filename,
                section_label=chunk.section_label,
                text=chunk.text[:1500],
                score=round(score, 4),
            )
        )

    return results


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())
