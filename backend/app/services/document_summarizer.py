from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from openai import AsyncOpenAI

from .config import config


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DocumentSummary:
    description: str
    summary: str


class DocumentSummarizer:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)

    async def summarize_document(self, text_content: str, filename: str) -> DocumentSummary:
        logger.info(f"Generating summary for document: {filename}")

        cleaned_text = text_content.strip()
        if not cleaned_text:
            fallback = self._generate_fallback_description(filename)
            return DocumentSummary(description=fallback, summary=fallback)

        excerpt = cleaned_text[:6000]
        try:
            response = await self.client.chat.completions.create(
                model=config.openai_default_model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are helping students organize study material for a workshop. "
                            "Return valid JSON with keys `description` and `summary`. "
                            "`description` must be a short one-line label under 110 characters. "
                            "`summary` must be a crisp 3-4 sentence explanation of the document, "
                            "covering the topic, key ideas, and why it is useful for revision."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Filename: {filename}\n\nDocument excerpt:\n{excerpt}",
                    },
                ],
                max_tokens=220,
                temperature=0.2,
            )

            raw_content = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_content)
            description = str(parsed.get("description", "")).strip()
            summary = str(parsed.get("summary", "")).strip()

            fallback = self._generate_fallback_description(filename)
            if not description:
                description = fallback
            if not summary:
                summary = fallback

            if len(description) > 140:
                description = description[:137].rstrip() + "..."

            logger.debug(f"Generated summary metadata for {filename}")
            return DocumentSummary(description=description, summary=summary)

        except Exception as e:
            logger.exception(f"Error generating summary for {filename}: {e}")
            fallback = self._generate_fallback_description(filename)
            return DocumentSummary(description=fallback, summary=fallback)

    @staticmethod
    def _generate_fallback_description(filename: str) -> str:
        logger.debug(f"Generating fallback description for {filename}")

        file_path = Path(filename)
        extension = file_path.suffix.lower()
        name_part = file_path.stem

        type_descriptions = {
            ".pdf": "PDF study material",
            ".txt": "Text study material",
            ".md": "Markdown study material",
            ".html": "Web study material",
            ".docx": "Word study material",
            ".json": "Structured study material",
        }

        type_desc = type_descriptions.get(extension, "Study material")

        if any(keyword in name_part.lower() for keyword in ["notes", "note"]):
            return f"Study notes covering {name_part.replace('-', ' ').replace('_', ' ')}"
        if any(keyword in name_part.lower() for keyword in ["lecture", "slides"]):
            return f"Lecture material on {name_part.replace('-', ' ').replace('_', ' ')}"
        if any(keyword in name_part.lower() for keyword in ["textbook", "book", "chapter"]):
            return f"Textbook-style material on {name_part.replace('-', ' ').replace('_', ' ')}"
        return f"{type_desc} for {name_part.replace('-', ' ').replace('_', ' ')}"


document_summarizer = DocumentSummarizer()

__all__ = ["DocumentSummarizer", "DocumentSummary", "document_summarizer"]
