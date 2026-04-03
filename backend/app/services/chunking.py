from __future__ import annotations

from app.models.document import DocumentChunk
from app.services.config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(text: str, document_id: str, filename: str) -> list[DocumentChunk]:
    words = text.split()
    if not words:
        return []

    chunks: list[DocumentChunk] = []
    start = 0
    idx = 0

    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_words = words[start:end]
        chunk_text_str = " ".join(chunk_words)

        section_label = f"chunk-{idx + 1}"

        chunks.append(
            DocumentChunk(
                document_id=document_id,
                filename=filename,
                section_label=section_label,
                text=chunk_text_str,
                index=idx,
            )
        )

        idx += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks
