from __future__ import annotations

import json
from pathlib import Path

from app.models.document import DocumentChunk, DocumentMetadata
from app.services.config import APP_DATA_DIR


def _meta_path(doc_id: str) -> Path:
    return APP_DATA_DIR / "metadata" / f"{doc_id}.json"


def _chunks_path(doc_id: str) -> Path:
    return APP_DATA_DIR / "chunks" / f"{doc_id}.json"


def _original_path(doc_id: str, filename: str) -> Path:
    return APP_DATA_DIR / "originals" / f"{doc_id}_{filename}"


def save_original(doc_id: str, filename: str, content: bytes) -> Path:
    path = _original_path(doc_id, filename)
    path.write_bytes(content)
    return path


def get_original_path(doc_id: str) -> Path | None:
    meta = load_metadata(doc_id)
    if meta is None:
        return None
    path = _original_path(doc_id, meta.filename)
    return path if path.exists() else None


def save_metadata(meta: DocumentMetadata) -> None:
    _meta_path(meta.id).write_text(meta.model_dump_json(indent=2), encoding="utf-8")


def load_metadata(doc_id: str) -> DocumentMetadata | None:
    path = _meta_path(doc_id)
    if not path.exists():
        return None
    return DocumentMetadata.model_validate_json(path.read_text(encoding="utf-8"))


def list_all_metadata() -> list[DocumentMetadata]:
    meta_dir = APP_DATA_DIR / "metadata"
    if not meta_dir.exists():
        return []
    results = []
    for f in sorted(meta_dir.glob("*.json")):
        try:
            results.append(DocumentMetadata.model_validate_json(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return results


def save_chunks(doc_id: str, chunks: list[DocumentChunk]) -> None:
    data = [c.model_dump() for c in chunks]
    _chunks_path(doc_id).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_chunks(doc_id: str) -> list[DocumentChunk]:
    path = _chunks_path(doc_id)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [DocumentChunk.model_validate(item) for item in data]


def load_all_chunks() -> list[DocumentChunk]:
    chunks_dir = APP_DATA_DIR / "chunks"
    if not chunks_dir.exists():
        return []
    all_chunks: list[DocumentChunk] = []
    for f in chunks_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            all_chunks.extend(DocumentChunk.model_validate(item) for item in data)
        except Exception:
            continue
    return all_chunks


def delete_document(doc_id: str) -> bool:
    meta = load_metadata(doc_id)
    if meta is None:
        return False

    _meta_path(doc_id).unlink(missing_ok=True)
    _chunks_path(doc_id).unlink(missing_ok=True)

    orig = _original_path(doc_id, meta.filename)
    if orig.exists():
        orig.unlink()

    return True
