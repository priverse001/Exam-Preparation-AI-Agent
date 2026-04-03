from __future__ import annotations

import logging
from pathlib import Path

from agents.mcp import MCPServerStdio

from ..services.config import config


logger = logging.getLogger(__name__)


notes_dir = Path(config.notes_dir)
notes_dir.mkdir(parents=True, exist_ok=True)

StudyNotesMCPServer = MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(notes_dir)],
    },
)


async def connect():
    try:
        if StudyNotesMCPServer.session is None:
            await StudyNotesMCPServer.connect()
            available_tools = await StudyNotesMCPServer.list_tools()
            logger.info(f"Available tools: {[tool.name for tool in available_tools]}")
            logger.info(f"Study Notes MCP Server connected successfully at {notes_dir}")
        else:
            logger.debug("Study Notes MCP already connected")
    except Exception as e:
        logger.error(f"Error connecting to Study Notes MCP Server: {e}")
        await StudyNotesMCPServer.cleanup()
