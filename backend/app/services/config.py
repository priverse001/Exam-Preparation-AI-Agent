from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import find_dotenv
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        dotenv_path = find_dotenv()
        if dotenv_path:
            logger.debug(f"Loading environment from {dotenv_path}")
            load_dotenv(dotenv_path)
        else:
            logger.warning("No .env file found")

        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        self.openai_default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")
        self.logfire_token = os.getenv("LOGFIRE_TOKEN", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        self.project_root = Path(__file__).resolve().parents[3]
        self.data_dir = Path(os.getenv("APP_DATA_DIR", self.project_root / "data"))
        self.upload_dir = self.data_dir / "uploaded_files"
        self.notes_dir = Path(os.getenv("APP_NOTES_DIR", self.project_root / "workshop_notes"))

    @staticmethod
    def _get_required_env(key: str) -> str:
        value = os.getenv(key)
        if not value:
            logger.error(f"Required environment variable {key} is not set")
            raise RuntimeError(
                f"{key} is not set. Please copy .env.template to .env and set this variable. "
                f"See README.md for setup instructions."
            )
        logger.info(f"Required environment variable {key} loaded successfully")
        return value

    def validate(self) -> bool:
        logger.info("Validating configuration")
        try:
            self._get_required_env("OPENAI_API_KEY")
            logger.info("Configuration validation successful")
            return True
        except RuntimeError:
            logger.exception("Configuration validation failed")
            return False


config = Config()
