from __future__ import annotations

from agents import function_tool

from app.models.document import SearchResult
from app.services import document_store, retrieval


@function_tool
def search_uploaded_materials(query: str) -> str:
    """Search through all uploaded study materials for content relevant to the query.

    Args:
        query: The search query describing what information you need.

    Returns:
        Formatted search results with citations.
    """
    results: list[SearchResult] = retrieval.search(query, top_k=5)

    if not results:
        return "No relevant content found in the uploaded materials."

    parts: list[str] = []
    for r in results:
        parts.append(f"[Source: {r.filename} | {r.section_label}]\n{r.text}\n")

    return "\n---\n".join(parts)


@function_tool
def list_uploaded_materials() -> str:
    """List all documents that have been uploaded to the system.

    Returns:
        A formatted list of all uploaded documents with their summaries.
    """
    docs = document_store.list_all_metadata()

    if not docs:
        return "No documents have been uploaded yet. Ask the user to upload study materials first."

    lines: list[str] = []
    for doc in docs:
        lines.append(f"- **{doc.filename}** (id: {doc.id}): {doc.description or doc.summary[:80]}")

    return f"Uploaded documents ({len(docs)} total):\n" + "\n".join(lines)
