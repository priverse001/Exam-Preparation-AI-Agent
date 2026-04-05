# Study Assistant Boilerplate Implementation Spec

## Purpose

This document describes the target shape of a fresh repository that recreates the important ideas from this workshop project without carrying over incidental implementation details or local generated files.

The target repo should be a workshop-friendly starter for:

- LLM basics
- OpenAI Agents SDK
- tool calling
- local RAG
- MCP filesystem integration
- FastAPI backend
- React frontend

## Product Summary

Build a web app where students can:

1. Upload study materials such as PDF, TXT, MD, HTML, DOCX, and JSON files.
2. See uploaded documents with generated summaries.
3. Ask grounded questions about uploaded materials in a chat UI.
4. Ask the system to create markdown revision notes and save them locally using MCP filesystem tools.

The implementation should be local-first and workshop-friendly:

- local file persistence
- local retrieval/indexing
- minimal cloud dependencies
- only OpenAI API required

## Core User Experience

### Main workflow

1. User opens the app.
2. User uploads one or more study documents.
3. Backend extracts text and generates a short summary.
4. Backend chunks and indexes the content locally.
5. User asks questions in chat.
6. Agent answers only from uploaded material and cites sources.
7. User asks to create revision notes.
8. Notes agent writes a markdown file in a local notes folder through MCP.

### Key UX requirements

- Clear upload flow
- Chat-first interface
- Visible list of uploaded documents
- Document preview support
- Source-grounded answers with citations
- Friendly workshop-oriented copy

## Architecture Overview

### High-level architecture

- `frontend/`: React + TypeScript app
- `backend/`: FastAPI app
- `resources/`: workshop docs, examples, presentation support
- root-level Python project config using `uv`

### Main backend areas

- API app and route registration
- document ingestion pipeline
- local retrieval service
- agent definitions and prompts
- MCP server integration
- chat streaming integration

### Main frontend areas

- chat panel
- file upload
- document list and preview
- theme support
- simple API integration

## Recommended Tech Stack

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- OpenAI Python SDK
- OpenAI Agents SDK
- `python-dotenv`
- `pypdf`
- `python-docx`
- `anyio`
- optional `logfire`

### Frontend

- React
- TypeScript
- Vite
- `@openai/chatkit-react`

### Tooling

- `uv` for Python dependency management
- `npm` for frontend and root JS scripts
- Docker / devcontainer for workshop setup
- `ruff`, `mypy`, `pytest`, `pre-commit`
- `.nvmrc` for Node.js version pinning
- optional `logfire` for tracing

## Monorepo Layout

```text
repo/
  backend/
    app/
      agents_sdk/
      models/
      routers/
      services/
      main.py
  frontend/
    src/
  resources/
    documents/
    code_examples/
  .devcontainer/
  pyproject.toml
  uv.lock
  package.json
  Dockerfile
  docker-compose.yml
  .nvmrc
  .pre-commit-config.yaml
  ruff.toml
  README.md
  .env.template
```

The new repo should copy the `resources/` directory contents as-is from the source workshop repo unless there is a strong reason to trim it.

## Required Backend Features

### API endpoints

Expose the backend under a single prefix such as `/exam-assistant`.

Required endpoints:

- `POST /exam-assistant/chatkit`
- `GET /exam-assistant/health`
- `GET /exam-assistant/documents`
- `POST /exam-assistant/documents/upload`
- `GET /exam-assistant/documents/{id}`
- `GET /exam-assistant/documents/{id}/file`
- `DELETE /exam-assistant/documents/{id}`

### Document ingestion

The backend must:

- accept uploads for `pdf`, `txt`, `md`, `html`, `docx`, `json`
- save originals locally
- extract text
- generate short summary metadata
- chunk text into overlapping searchable sections
- persist metadata and chunks locally

### Local retrieval

The backend should implement a simple local search layer. A full embedding/vector database is not required for the boilerplate.

The search system should:

- search over chunked text
- return best matches
- include filename and section labels
- support citations in final answers

### Agent system

Create three agents:

1. `TriageAgent`
2. `CourseMaterialAgent`
3. `RevisionNotesAgent`

#### Triage agent

Responsibilities:

- route content questions to `CourseMaterialAgent`
- route note creation/export/save requests to `RevisionNotesAgent`
- keep handoffs invisible to the user

#### Course material agent

Responsibilities:

- answer only from uploaded material
- summarize uploaded content
- explain concepts in student-friendly language
- cite factual statements

Tools:

- `search_uploaded_materials`
- `list_uploaded_materials`

#### Revision notes agent

Responsibilities:

- create markdown revision notes
- save notes only within a safe notes directory
- use retrieved content before writing notes when content grounding is required

Tools:

- `search_uploaded_materials`
- `list_uploaded_materials`
- MCP filesystem tools

## Prompting Requirements

All agent prompts should use strong, explicit instructions.

Each agent prompt should include:

- clear role definition
- explicit workflow
- tool usage rules
- edge-case behavior
- response formatting requirements

### Important prompt guardrails

- always use retrieval before content answers
- do not invent facts
- say when uploaded material is insufficient
- always cite sources for factual claims
- only write notes inside the allowed notes directory

## MCP Requirements

Use the filesystem MCP server as the workshop MCP integration.

Requirements:

- scope filesystem access to one notes directory only
- create markdown files only in that directory
- do not depend on third-party SaaS tools for the workshop-critical flow

## Frontend Requirements

### Main screens/components

- chat panel
- study documents panel
- file upload
- document preview modal
- optional theme toggle

### Frontend behavior

- load documents on startup
- upload files through backend
- refresh document list after upload/delete
- preview files inline where practical
- connect chat UI to backend streaming endpoint

## Configuration Requirements

Use environment variables for:

- `OPENAI_API_KEY`
- optional model override
- optional data directory override
- optional notes directory override
- optional `LOGFIRE_TOKEN`
- optional `LOG_LEVEL`

Provide:

- `.env.template`
- clear README setup steps
- Docker/devcontainer workflow

### Node version management

- Include an `.nvmrc` pinned to Node.js 22

### Dev tooling config

- Include `.pre-commit-config.yaml`
- Include `ruff.toml`
- Configure linting/formatting so a contributor can run checks immediately

## Development Requirements

### Root Python project

Use a root-level `pyproject.toml` and root `uv.lock` so editors auto-detect the top-level `.venv`.

### Root scripts

Have one root `npm run start` script that starts:

- backend server
- frontend dev server

### Recommended developer experience

- devcontainer support
- `uv sync`
- `npm install`
- `npm run start`
- `pre-commit install`

### Observability

- Include optional backend `logfire` integration
- Application must still run normally when `LOGFIRE_TOKEN` is not set

## Suggested Workshop Checkpoints

### Checkpoint 0: Repo scaffold

- monorepo created
- root Python config
- frontend and backend boot

### Checkpoint 1: Basic chat completion

- simple script using OpenAI chat completions

### Checkpoint 2: Multi-turn memory

- demonstrate manual history handling

### Checkpoint 3: First tool

- agent can call one tool

### Checkpoint 4: Structured output

- agent returns a typed Pydantic object

### Checkpoint 5: Single study assistant

- simple study helper over toy knowledge

### Checkpoint 6: Multi-tool agent

- agent combines multiple tools

### Checkpoint 7: Multi-agent routing

- coordinator + specialists + handoffs

### Checkpoint 8: Real document ingestion

- upload, extract, summarize, chunk, persist

### Checkpoint 9: Local RAG

- grounded answers from uploaded content with citations

### Checkpoint 10: MCP notes agent

- create revision notes as markdown through filesystem MCP

### Checkpoint 11: Full web app

- chat + upload + document library + preview

### Checkpoint 12: Workshop hardening

- docs, setup, Docker, starter prompts, examples

## Non-Goals

The fresh boilerplate should not optimize for:

- enterprise auth
- multi-tenant permissions
- production vector search
- cloud storage
- advanced background processing
- large-scale observability

## Acceptance Criteria

The boilerplate is complete when:

1. A new user can clone the repo, set `OPENAI_API_KEY`, and run it locally or in a container.
2. The frontend can upload and display study documents.
3. The backend can extract, summarize, chunk, and index documents locally.
4. The chat agent answers only from uploaded material and cites sources.
5. The notes agent can create markdown revision notes through MCP.
6. The project is understandable enough to teach from in a workshop.
7. The repo includes baseline tooling and config for `pre-commit`, `ruff`, `.nvmrc`, Docker, and devcontainer support.
