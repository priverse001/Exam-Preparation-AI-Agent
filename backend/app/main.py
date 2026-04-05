from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents_sdk.mcp import connect_mcp
from app.routers import chat, documents
from app.services.config import LOG_LEVEL, LOGFIRE_TOKEN, ensure_dirs

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)

# Optional logfire tracing (Presentation Slide 19: Tracing and Debugging)
if LOGFIRE_TOKEN:
    try:
        import logfire

        logfire.configure()
        logfire.instrument_fastapi()
        logfire.instrument_openai_agents()
        logger.info("Logfire tracing enabled (FastAPI + Agents SDK)")
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
    try:
        await connect_mcp()
        logger.info("Filesystem MCP preconnected during startup")
    except Exception as e:
        logger.warning(f"Filesystem MCP preconnect failed at startup: {e}")
    logger.info("Study Assistant backend started")


@app.get("/exam-assistant/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
