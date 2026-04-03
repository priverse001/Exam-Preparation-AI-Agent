from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_DEFAULT_MODEL: str = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")

APP_DATA_DIR: Path = Path(os.getenv("APP_DATA_DIR", "./data"))
APP_NOTES_DIR: Path = Path(os.getenv("APP_NOTES_DIR", "./workshop_notes"))

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOGFIRE_TOKEN: str = os.getenv("LOGFIRE_TOKEN", "")

SUPPORTED_EXTENSIONS: set[str] = {".pdf", ".txt", ".md", ".html", ".docx", ".json"}

CHUNK_SIZE: int = 800
CHUNK_OVERLAP: int = 200


def ensure_dirs() -> None:
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (APP_DATA_DIR / "originals").mkdir(exist_ok=True)
    (APP_DATA_DIR / "metadata").mkdir(exist_ok=True)
    (APP_DATA_DIR / "chunks").mkdir(exist_ok=True)
    APP_NOTES_DIR.mkdir(parents=True, exist_ok=True)
