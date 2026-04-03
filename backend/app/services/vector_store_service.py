from __future__ import annotations

import json
import logging
import re
import time
import uuid
from dataclasses import asdict
from dataclasses import dataclass
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from typing import Any

import anyio
from docx import Document as DocxDocument
from pypdf import PdfReader

from ..models.document_metadata import DocumentMetadata
from ..models.document_metadata import metadata_store
from .config import config
from .document_summarizer import document_summarizer


logger = logging.getLogger(__name__)

TOKEN_PATTERN = re.compile(r"[a-z0-9]{2,}")
WHITESPACE_PATTERN = re.compile(r"\s+")

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "with",
    "your",
}


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())

    def get_text(self) -> str:
        return " ".join(self.parts)


@dataclass(frozen=True, slots=True)
class VectorStoreFile:
    id: str
    filename: str
    bytes: int
    created_at: int
    status: str
    usage_bytes: int | None = None
    object: str = "local_store.file"


@dataclass(frozen=True, slots=True)
class VectorStoreInfo:
    id: str
    name: str | None
    file_counts: dict[str, int]
    status: str
    created_at: int
    usage_bytes: int
    object: str = "local_store"


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    id: str
    file_id: str
    filename: str
    citation: str
    text: str
    position: int
    token_count: int


class VectorStoreService:
    def __init__(self):
        self.data_dir = config.data_dir
        self.upload_dir = config.upload_dir
        self.text_dir = self.data_dir / "extracted_text"
        self.index_path = self.data_dir / "document_chunks.json"
        self.store_name = "local-study-material-index"
        self._chunks_by_file: dict[str, list[DocumentChunk]] = {}

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.text_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_chunks()

    def _load_chunks(self) -> None:
        if not self.index_path.exists():
            self._chunks_by_file = {}
            return

        try:
            with open(self.index_path, encoding="utf-8") as f:
                data = json.load(f)
            self._chunks_by_file = {
                file_id: [DocumentChunk(**chunk_dict) for chunk_dict in chunk_dicts]
                for file_id, chunk_dicts in data.items()
            }
        except Exception as e:
            logger.exception(f"Failed to load local document index: {e}")
            self._chunks_by_file = {}

    def _save_chunks(self) -> None:
        data = {file_id: [asdict(chunk) for chunk in chunks] for file_id, chunks in self._chunks_by_file.items()}
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def get_vector_store_info(self) -> VectorStoreInfo:
        files = await self.list_vector_store_files(limit=1000)
        return VectorStoreInfo(
            id="local-store",
            name=self.store_name,
            file_counts={"completed": len(files)},
            status="ready",
            created_at=int(self.index_path.stat().st_mtime) if self.index_path.exists() else int(time.time()),
            usage_bytes=sum(file.bytes for file in files),
        )

    async def list_vector_store_files(
        self,
        limit: int = 20,
        order: str = "desc",
        after: str | None = None,
        before: str | None = None,
    ) -> list[VectorStoreFile]:
        del after, before

        files: list[VectorStoreFile] = []
        for metadata in metadata_store.list_metadata():
            file_path = Path(metadata.local_file_path) if metadata.local_file_path else None
            created_at = metadata.upload_time
            size = metadata.file_size
            if file_path and file_path.exists():
                size = file_path.stat().st_size
            files.append(
                VectorStoreFile(
                    id=metadata.file_id,
                    filename=metadata.original_filename,
                    bytes=size,
                    created_at=created_at,
                    status="processed",
                    usage_bytes=size,
                )
            )

        files.sort(key=lambda file: file.created_at, reverse=(order == "desc"))
        return files[:limit]

    async def delete_file_from_vector_store(self, file_id: str) -> bool:
        removed = self._chunks_by_file.pop(file_id, None)
        if removed is not None:
            self._save_chunks()
            return True
        return False

    async def delete_file_from_openai(self, file_id: str) -> bool:
        del file_id
        return False

    async def delete_file_completely(self, file_id: str) -> dict[str, bool]:
        results = {"vector_store": False, "openai_files": False, "local_storage": False}

        metadata = metadata_store.get_metadata(file_id)
        results["vector_store"] = await self.delete_file_from_vector_store(file_id)

        if metadata and metadata.extracted_text_path:
            text_path = Path(metadata.extracted_text_path)
            if text_path.exists():
                text_path.unlink()

        if metadata and metadata.local_file_path:
            local_path = Path(metadata.local_file_path)
            if local_path.exists():
                local_path.unlink()
                results["local_storage"] = True

        return results

    async def get_file_info(self, file_id: str) -> VectorStoreFile:
        metadata = metadata_store.get_metadata(file_id)
        if metadata is None:
            raise RuntimeError(f"Failed to retrieve file info: {file_id} not found")

        file_path = Path(metadata.local_file_path) if metadata.local_file_path else None
        size = metadata.file_size
        if file_path and file_path.exists():
            size = file_path.stat().st_size

        return VectorStoreFile(
            id=metadata.file_id,
            filename=metadata.original_filename,
            bytes=size,
            created_at=metadata.upload_time,
            status="processed",
            usage_bytes=size,
        )

    async def add_file_to_vector_store(
        self,
        file_content: bytes,
        filename: str,
        file_extension: str,
    ) -> dict[str, Any]:
        logger.info(f"Adding file to local knowledge base: {filename} ({len(file_content)} bytes)")

        file_id = f"doc_{uuid.uuid4().hex[:12]}"
        file_path = self.upload_dir / f"{file_id}_{Path(filename).name}"
        async with await anyio.open_file(file_path, "wb") as local_file:
            await local_file.write(file_content)

        extracted_text = self._extract_text(file_content=file_content, filename=filename, extension=file_extension)
        extracted_text_path = self.text_dir / f"{file_id}.txt"
        async with await anyio.open_file(extracted_text_path, "w", encoding="utf-8") as text_file:
            await text_file.write(extracted_text)

        summary = await document_summarizer.summarize_document(extracted_text, filename)
        chunks = self._build_chunks(file_id=file_id, filename=filename, text=extracted_text)
        self._chunks_by_file[file_id] = chunks
        self._save_chunks()

        metadata = DocumentMetadata(
            file_id=file_id,
            original_filename=filename,
            title=Path(filename).stem,
            description=summary.description,
            summary=summary.summary,
            file_size=len(file_content),
            upload_time=int(time.time()),
            file_type=file_extension,
            chunk_count=len(chunks),
            local_file_path=str(file_path),
            extracted_text_path=str(extracted_text_path),
        )
        metadata_store.store_metadata(metadata)

        return {
            "message": "File uploaded successfully",
            "file": {
                "id": file_id,
                "filename": filename,
                "title": metadata.title,
                "description": metadata.description,
                "summary": metadata.summary,
                "bytes": len(file_content),
                "status": "processed",
                "chunk_count": metadata.chunk_count,
            },
        }

    def search_documents(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            return []

        query_tokens = [token for token in TOKEN_PATTERN.findall(normalized_query) if token not in STOP_WORDS]
        results: list[tuple[float, DocumentChunk]] = []

        for chunks in self._chunks_by_file.values():
            for chunk in chunks:
                score = self._score_chunk(chunk=chunk, query=normalized_query, query_tokens=query_tokens)
                if score <= 0:
                    continue
                results.append((score, chunk))

        results.sort(key=lambda item: (item[0], -item[1].position), reverse=True)

        top_results: list[dict[str, Any]] = []
        for score, chunk in results[:limit]:
            top_results.append(
                {
                    "file_id": chunk.file_id,
                    "filename": chunk.filename,
                    "citation": chunk.citation,
                    "excerpt": chunk.text,
                    "score": round(score, 2),
                }
            )
        return top_results

    @staticmethod
    def _score_chunk(chunk: DocumentChunk, query: str, query_tokens: list[str]) -> float:
        haystack = chunk.text.lower()
        filename = chunk.filename.lower()

        score = 0.0
        if query in haystack:
            score += 10.0

        for token in query_tokens:
            occurrences = haystack.count(token)
            if occurrences:
                score += min(occurrences, 4) * 2.0
            if token in filename:
                score += 1.5

        if len(query_tokens) >= 2 and all(token in haystack for token in query_tokens):
            score += 3.0

        return score

    def _extract_text(self, file_content: bytes, filename: str, extension: str) -> str:
        logger.info(f"Extracting text from {filename}")
        if extension in {".txt", ".md"}:
            return self._clean_text(file_content.decode("utf-8", errors="ignore"))
        if extension == ".json":
            raw_json = json.loads(file_content.decode("utf-8", errors="ignore"))
            return self._clean_text(json.dumps(raw_json, indent=2, ensure_ascii=False))
        if extension == ".html":
            parser = _HTMLTextExtractor()
            parser.feed(file_content.decode("utf-8", errors="ignore"))
            return self._clean_text(parser.get_text())
        if extension == ".pdf":
            reader = PdfReader(BytesIO(file_content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return self._clean_text(text)
        if extension == ".docx":
            document = DocxDocument(BytesIO(file_content))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
            return self._clean_text(text)

        raise RuntimeError(f"Unsupported file type for extraction: {extension}")

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\x00", " ")
        text = WHITESPACE_PATTERN.sub(" ", text)
        return text.strip()

    @staticmethod
    def _build_chunks(
        file_id: str, filename: str, text: str, chunk_size: int = 900, overlap: int = 120
    ) -> list[DocumentChunk]:
        if not text:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        position = 1

        while start < len(text):
            end = min(len(text), start + chunk_size)
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        id=f"{file_id}_chunk_{position}",
                        file_id=file_id,
                        filename=filename,
                        citation=f"section {position}",
                        text=chunk_text,
                        position=position,
                        token_count=len(TOKEN_PATTERN.findall(chunk_text.lower())),
                    )
                )
                position += 1

            if end >= len(text):
                break
            start = max(end - overlap, start + 1)

        return chunks


def as_file_dicts(files: list[VectorStoreFile]) -> list[dict[str, Any]]:
    return [
        {
            "id": file.id,
            "filename": file.filename,
            "bytes": file.bytes,
            "created_at": file.created_at,
            "status": file.status,
            "usage_bytes": file.usage_bytes,
            "object": file.object,
        }
        for file in files
    ]


vector_store_service = VectorStoreService()


__all__ = [
    "DocumentChunk",
    "VectorStoreFile",
    "VectorStoreInfo",
    "VectorStoreService",
    "as_file_dicts",
    "vector_store_service",
]
