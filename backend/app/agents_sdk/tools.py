from __future__ import annotations

from agents import function_tool
from pydantic import BaseModel, Field

from app.models.document import SearchResult
from app.services import document_store, retrieval


# ---------------------------------------------------------------------------
# Structured Output Models – demonstrates Pydantic-based structured outputs
# (Presentation Slide 9: Structured Outputs)
# ---------------------------------------------------------------------------


class TopicSummary(BaseModel):
    """Structured summary of a study topic, returned by the generate_topic_summary tool."""

    # >>> EXERCISE_1_START
    topic: str = Field(description="The main topic being summarized")
    key_concepts: list[str] = Field(description="3-5 key concepts or terms")
    summary: str = Field(description="A concise 2-3 sentence summary")
    difficulty_level: str = Field(description="beginner, intermediate, or advanced")
    # >>> EXERCISE_1_END


@function_tool
def generate_topic_summary(topic: str, content: str) -> TopicSummary:
    """Generate a structured summary for a study topic based on provided content.

    Use this after retrieving content with search_uploaded_materials to create
    a well-organized topic breakdown.

    Args:
        topic: The topic being summarized.
        content: The source content to summarize (from search results).

    Returns:
        A structured TopicSummary with key concepts, summary, and difficulty level.
    """
    # The LLM fills in the structured fields via function calling;
    # this fallback is used if the tool is called directly.
    # >>> EXERCISE_4_START
    return TopicSummary(
        topic=topic,
        key_concepts=[topic],
        summary=content[:200] if len(content) > 200 else content,
        difficulty_level="intermediate",
    )
    # >>> EXERCISE_4_END


@function_tool
def search_uploaded_materials(query: str) -> str:
    """Search through all uploaded study materials for content relevant to the query.

    Args:
        query: The search query describing what information you need.

    Returns:
        Formatted search results with citations.
    """
    # >>> EXERCISE_2_START
    results: list[SearchResult] = retrieval.search(query, top_k=5)

    if not results:
        return "No relevant content found in the uploaded materials."

    parts: list[str] = []
    for r in results:
        parts.append(f"[Source: {r.filename} | {r.section_label}]\n{r.text}\n")

    return "\n---\n".join(parts)
    # >>> EXERCISE_2_END


@function_tool
def list_uploaded_materials() -> str:
    """List all documents that have been uploaded to the system.

    Returns:
        A formatted list of all uploaded documents with their summaries.
    """
    # >>> EXERCISE_3_START
    docs = document_store.list_all_metadata()

    if not docs:
        return "No documents have been uploaded yet. Ask the user to upload study materials first."

    lines: list[str] = []
    for doc in docs:
        lines.append(f"- **{doc.filename}** (id: {doc.id}): {doc.description or doc.summary[:80]}")

    return f"Uploaded documents ({len(docs)} total):\n" + "\n".join(lines)
    # >>> EXERCISE_3_END
