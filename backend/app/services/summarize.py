from __future__ import annotations

from openai import AsyncOpenAI

from app.services.config import OPENAI_API_KEY, OPENAI_DEFAULT_MODEL

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    return _client


async def generate_summary(text: str, filename: str) -> tuple[str, str]:
    """Generate a short summary and one-line description for a document.

    Returns (summary, description).
    """
    preview = text[:3000]
    client = _get_client()

    resp = await client.chat.completions.create(
        model=OPENAI_DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that summarizes study documents for university students. "
                    "Given extracted text from a document, produce:\n"
                    "1. A one-line DESCRIPTION (max 15 words) of what the document covers.\n"
                    "2. A SHORT SUMMARY (3-5 sentences) of the key topics.\n\n"
                    "Respond in exactly this format:\n"
                    "DESCRIPTION: <your description>\n"
                    "SUMMARY: <your summary>"
                ),
            },
            {"role": "user", "content": f"Filename: {filename}\n\nExtracted text:\n{preview}"},
        ],
        temperature=0.3,
        max_tokens=300,
    )

    content = resp.choices[0].message.content or ""

    description = ""
    summary = ""
    for line in content.split("\n"):
        line = line.strip()
        if line.upper().startswith("DESCRIPTION:"):
            description = line.split(":", 1)[1].strip()
        elif line.upper().startswith("SUMMARY:"):
            summary = line.split(":", 1)[1].strip()

    if not summary:
        summary = content[:500]
    if not description:
        description = filename

    return summary, description
