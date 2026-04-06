from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import _logfire_setup

from agents import Agent
from agents import Runner
from agents.mcp import MCPServerStdio

logger = logging.getLogger("workshop.mcp")


async def main():
    repo_path = Path(__file__).resolve().parent.parent.parent.resolve()

    logger.info(f"Allowing MCP the access to {repo_path=}")

    async with MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(repo_path)],
        },
    ) as FileSystemMCPServer:
        agent = Agent(
            name="File System Agent",
            instructions="You are a file system agent with access to files allowed. Answer any queries about the files",
            mcp_servers=[FileSystemMCPServer],
        )
        tools = await FileSystemMCPServer.list_tools()

        logger.info("Available MCP tools:")
        for tool in tools:
            logger.info("- %s: %s", tool.name, tool.description)

        logger.info("=" * 120)

        result = await Runner.run(agent, "List the top-level files and directories in this project")
        logger.info(result.final_output)


if __name__ == "__main__":
    asyncio.run(_logfire_setup.run_example("8_mcp", main()))
