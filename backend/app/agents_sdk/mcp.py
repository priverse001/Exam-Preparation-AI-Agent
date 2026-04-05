from __future__ import annotations

import logging

from agents.mcp import MCPServerStdio

from app.agents_sdk.agents import revision_notes_agent
from app.services.config import APP_NOTES_DIR

logger = logging.getLogger(__name__)

MCP_CONNECT_TIMEOUT_SECONDS = 30

# >>> EXERCISE_7A_START
filesystem_mcp_server = MCPServerStdio(
    name="filesystem",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(APP_NOTES_DIR.resolve())],
    },
    cache_tools_list=True,
    client_session_timeout_seconds=MCP_CONNECT_TIMEOUT_SECONDS,
    max_retry_attempts=2,
    tool_filter={
        "allowed_tool_names": [
            "write_file",
            "edit_file",
            "create_directory",
            "list_allowed_directories",
        ]
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
            logger.info("Filesystem MCP connected. Tools: %s", [t.name for t in available_tools])
        else:
            logger.debug("Filesystem MCP already connected")
            if revision_notes_agent.mcp_servers != [filesystem_mcp_server]:
                revision_notes_agent.mcp_servers = [filesystem_mcp_server]
    except Exception:
        logger.exception("Failed to connect filesystem MCP")
        revision_notes_agent.mcp_servers = []
        await filesystem_mcp_server.cleanup()
        raise
    # >>> EXERCISE_7B_END
