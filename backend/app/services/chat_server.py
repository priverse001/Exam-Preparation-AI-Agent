"""ChatKit server that runs the study assistant agent pipeline."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from agents import Agent, Runner
from agents.lifecycle import RunHooks
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem

from app.agents_sdk.agents import triage_agent
from app.agents_sdk.mcp import connect_mcp
from app.services.chat_store import InMemoryStore

logger = logging.getLogger(__name__)

_store = InMemoryStore()


# ---------------------------------------------------------------------------
# Demo logging hooks — prints agent lifecycle events to the terminal
# so the instructor can show students what's happening behind the scenes.
# ---------------------------------------------------------------------------
class DemoLoggingHooks(RunHooks[Any]):
    async def on_agent_start(self, context, agent: Agent) -> None:
        logger.info(f"🤖 Agent started: {agent.name}")

    async def on_agent_end(self, context, agent: Agent, output) -> None:
        preview = str(output)[:120] if output else "(no output)"
        logger.info(f"✅ Agent done:    {agent.name} → {preview}")

    async def on_handoff(self, context, from_agent: Agent, to_agent: Agent) -> None:
        logger.info(f"🔀 Handoff:       {from_agent.name} → {to_agent.name}")

    async def on_tool_start(self, context, agent: Agent, tool) -> None:
        logger.info(f"🔧 Tool call:     {agent.name} → {tool.name}")

    async def on_tool_end(self, context, agent: Agent, tool, result) -> None:
        preview = str(result)[:100] if result else "(empty)"
        logger.info(f"   Tool result:   {tool.name} → {preview}")


_hooks = DemoLoggingHooks()


class StudyAssistantServer(ChatKitServer[dict[str, Any]]):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        if input_user_message is None:
            return

        await connect_mcp()

        items_page = await self.store.load_thread_items(thread.id, after=None, limit=100, order="asc", context=context)
        input_items = await simple_to_agent_input(items_page.data)

        agent_context = AgentContext(thread=thread, store=self.store, request_context=context)

        result = Runner.run_streamed(triage_agent, input=input_items, context=agent_context, hooks=_hooks)
        async for event in stream_agent_response(agent_context, result):
            yield event


_server = StudyAssistantServer(store=_store)


def get_server() -> StudyAssistantServer:
    return _server
