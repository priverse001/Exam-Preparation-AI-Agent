from __future__ import annotations

import logging

from agents import Agent

from . import prompts
from .mcp import StudyNotesMCPServer
from .tools import list_uploaded_materials
from .tools import search_uploaded_materials


logger = logging.getLogger(__name__)


AnswerStudentQueryAgent = Agent(
    name="Course Material Agent",
    handoff_description="Answers questions and summaries grounded in uploaded course material",
    instructions=prompts.QA_PROMPT,
    tools=[search_uploaded_materials, list_uploaded_materials],
)

RevisionNotesAgent = Agent(
    name="Revision Notes Agent",
    handoff_description="Creates markdown revision notes using MCP filesystem tools",
    instructions=prompts.NOTES_PROMPT,
    tools=[search_uploaded_materials, list_uploaded_materials],
    mcp_servers=[StudyNotesMCPServer],
)

TriageAgent = Agent(
    name="Workshop Triage Agent",
    instructions=prompts.TRIAGE_PROMPT,
    handoffs=[AnswerStudentQueryAgent, RevisionNotesAgent],
)
