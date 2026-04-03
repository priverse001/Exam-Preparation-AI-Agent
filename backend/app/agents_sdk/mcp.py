from __future__ import annotations

import logging

from agents.mcp import MCPServerStdio

from app.agents_sdk.agents import revision_notes_agent
from app.services.config import APP_NOTES_DIR

logger = logging.getLogger(__name__)

# >>> EXERCISE_7A_START
filesystem_mcp_server = MCPServerStdio(
    name="filesystem",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(APP_NOTES_DIR.resolve())],
    },
)
# >>> EXERCISE_7A_END


async def connect_mcp() -> None:
    """Connect the filesystem MCP server if not already connected."""
    # >>> EXERCISE_7B_START
    try:
        if filesystem_mcp_server.session is None:
            await filesystem_mcp_server.connect()
            revision_notes_agent.mcp_servers = [filesystem_mcp_server]
            available_tools = await filesystem_mcp_server.list_tools()
            logger.info(f"Filesystem MCP connected. Tools: {[t.name for t in available_tools]}")
        else:
            logger.debug("Filesystem MCP already connected")
    except Exception as e:
        logger.error(f"Failed to connect filesystem MCP: {e}")
        await filesystem_mcp_server.cleanup()
    # >>> EXERCISE_7B_END
