from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat, documents
from app.services.config import LOG_LEVEL, LOGFIRE_TOKEN, ensure_dirs

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)

# Optional logfire tracing
if LOGFIRE_TOKEN:
    try:
        import logfire

        logfire.configure()
        logfire.instrument_fastapi()
        logger.info("Logfire tracing enabled")
    except Exception as e:
        logger.warning(f"Logfire setup failed (non-critical): {e}")

app = FastAPI(title="Study Assistant AI Boilerplate")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.on_event("startup")
async def startup():
    ensure_dirs()
    logger.info("Study Assistant backend started")


@app.get("/exam-assistant/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
