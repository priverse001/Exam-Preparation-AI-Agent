from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    document_id: str
    filename: str
    section_label: str = ""
    text: str
    index: int = 0


class DocumentMetadata(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    filename: str
    content_type: str = ""
    size_bytes: int = 0
    summary: str = ""
    description: str = ""
    num_chunks: int = 0
    uploaded_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class UploadedDocumentResponse(BaseModel):
    id: str
    filename: str
    summary: str
    description: str
    num_chunks: int
    uploaded_at: str
    size_bytes: int = 0


class DocumentListResponse(BaseModel):
    documents: list[UploadedDocumentResponse]


class SearchResult(BaseModel):
    document_id: str
    filename: str
    section_label: str
    text: str
    score: float
