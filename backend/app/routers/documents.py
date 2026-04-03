from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.models.document import DocumentListResponse, DocumentMetadata, UploadedDocumentResponse
from app.services import document_store
from app.services.chunking import chunk_text
from app.services.config import SUPPORTED_EXTENSIONS
from app.services.extraction import extract_text
from app.services.summarize import generate_summary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exam-assistant/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    docs = document_store.list_all_metadata()
    return DocumentListResponse(
        documents=[
            UploadedDocumentResponse(
                id=d.id,
                filename=d.filename,
                summary=d.summary,
                description=d.description,
                num_chunks=d.num_chunks,
                uploaded_at=d.uploaded_at,
                size_bytes=d.size_bytes,
            )
            for d in docs
        ]
    )


@router.post("/upload", response_model=UploadedDocumentResponse)
async def upload_document(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    content = await file.read()
    meta = DocumentMetadata(filename=file.filename, content_type=file.content_type or "", size_bytes=len(content))

    original_path = document_store.save_original(meta.id, file.filename, content)

    try:
        text = extract_text(original_path)
    except Exception as e:
        logger.error(f"Text extraction failed for {file.filename}: {e}")
        text = ""

    if text:
        try:
            summary, description = await generate_summary(text, file.filename)
            meta.summary = summary
            meta.description = description
        except Exception as e:
            logger.error(f"Summary generation failed for {file.filename}: {e}")
            meta.summary = "Summary generation failed"
            meta.description = file.filename

        chunks = chunk_text(text, meta.id, file.filename)
        meta.num_chunks = len(chunks)
        document_store.save_chunks(meta.id, chunks)
    else:
        meta.summary = "Could not extract text from this file"
        meta.description = file.filename

    document_store.save_metadata(meta)

    return UploadedDocumentResponse(
        id=meta.id,
        filename=meta.filename,
        summary=meta.summary,
        description=meta.description,
        num_chunks=meta.num_chunks,
        uploaded_at=meta.uploaded_at,
        size_bytes=meta.size_bytes,
    )


@router.get("/{doc_id}", response_model=UploadedDocumentResponse)
async def get_document(doc_id: str):
    meta = document_store.load_metadata(doc_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return UploadedDocumentResponse(
        id=meta.id,
        filename=meta.filename,
        summary=meta.summary,
        description=meta.description,
        num_chunks=meta.num_chunks,
        uploaded_at=meta.uploaded_at,
        size_bytes=meta.size_bytes,
    )


@router.get("/{doc_id}/file")
async def get_document_file(doc_id: str):
    path = document_store.get_original_path(doc_id)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=path.name.split("_", 1)[-1])


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    if not document_store.delete_document(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted"}
