from __future__ import annotations

import logging
from typing import Any

from agents import function_tool

from ..models.document_metadata import metadata_store
from ..services.vector_store_service import vector_store_service


logger = logging.getLogger(__name__)


@function_tool
async def search_uploaded_materials(query: str) -> dict[str, Any]:
    """
    Search the locally uploaded study materials and return the most relevant excerpts.

    Args:
        query (str): The student question or concept to search for.
    """
    logger.info(f"Searching uploaded materials for query: {query}")
    matches = vector_store_service.search_documents(query=query, limit=4)
    return {"query": query, "matches": matches, "match_count": len(matches)}


@function_tool
async def list_uploaded_materials() -> dict[str, Any]:
    """
    List uploaded study materials with their short descriptions and summaries.
    """
    documents = []
    for metadata in sorted(metadata_store.list_metadata(), key=lambda item: item.upload_time, reverse=True):
        documents.append(
            {
                "file_id": metadata.file_id,
                "filename": metadata.original_filename,
                "title": metadata.title,
                "description": metadata.description,
                "summary": metadata.summary,
                "chunk_count": metadata.chunk_count,
            }
        )
    return {"documents": documents, "count": len(documents)}
