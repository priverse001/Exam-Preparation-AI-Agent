"""ChatKit server that runs the study assistant agent pipeline."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from agents import Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem

from app.agents_sdk.agents import triage_agent
from app.agents_sdk.mcp import connect_mcp
from app.services.chat_store import InMemoryStore

logger = logging.getLogger(__name__)

_store = InMemoryStore()


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

        result = Runner.run_streamed(triage_agent, input=input_items, context=agent_context)
        async for event in stream_agent_response(agent_context, result):
            yield event


_server = StudyAssistantServer(store=_store)


def get_server() -> StudyAssistantServer:
    return _server
