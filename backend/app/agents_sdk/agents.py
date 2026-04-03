from __future__ import annotations

from agents import Agent

from app.agents_sdk.prompts import (
    COURSE_MATERIAL_AGENT_PROMPT,
    REVISION_NOTES_AGENT_PROMPT,
    TRIAGE_AGENT_PROMPT,
)
from app.agents_sdk.tools import list_uploaded_materials, search_uploaded_materials
from app.services.config import OPENAI_DEFAULT_MODEL

course_material_agent = Agent(
    name="CourseMaterialAgent",
    instructions=COURSE_MATERIAL_AGENT_PROMPT,
    model=OPENAI_DEFAULT_MODEL,
    tools=[search_uploaded_materials, list_uploaded_materials],
)

revision_notes_agent = Agent(
    name="RevisionNotesAgent",
    instructions=REVISION_NOTES_AGENT_PROMPT,
    model=OPENAI_DEFAULT_MODEL,
    tools=[search_uploaded_materials, list_uploaded_materials],
    # MCP tools are added at runtime in create_triage_agent()
)

triage_agent = Agent(
    name="TriageAgent",
    instructions=TRIAGE_AGENT_PROMPT,
    model=OPENAI_DEFAULT_MODEL,
    handoffs=[
        course_material_agent,
        revision_notes_agent,
    ],
)
