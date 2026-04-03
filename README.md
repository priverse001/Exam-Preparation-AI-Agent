# IIT BHU AI Workshop

This branch is the working reference implementation for an IIT BHU workshop on agents, tools, RAG, and MCP.

The app is an AI course-material copilot:
- students upload notes or slides
- the backend extracts and summarizes them
- the agent answers questions with citations from uploaded material
- an MCP-powered notes agent can save revision notes as markdown files

## Branch Roles
- `master`: original reference implementation from the earlier workshop
- `workshop`: original student scaffold from the earlier workshop
- `iit-bhu`: IIT BHU student scaffold branch
- `iit-bhu-solution`: IIT BHU reference/solution branch

## Workshop Concepts
- `LLMs`: used for summary generation and grounded answers
- `Tools`: the study agent calls local retrieval tools
- `RAG`: uploaded material is chunked, indexed locally, and searched at answer time
- `MCP`: the notes agent uses filesystem MCP tools to create markdown revision sheets

## Recommended Setup

Use a dev container or Docker. The goal is to avoid Python/Node/tooling drift across student laptops.

### Prerequisites
- Docker Desktop or another Docker-compatible runtime
- Git
- An `OPENAI_API_KEY`

### Option 1: Dev Container
1. Copy `.env.template` to `.env`
2. Set `OPENAI_API_KEY` in `.env`
3. Open the repo in a devcontainer
4. In the container terminal, run `npm run start`
5. Open the forwarded frontend port in the browser

### Option 2: Plain Docker Compose
1. Copy `.env.template` to `.env`
2. Set `OPENAI_API_KEY` in `.env`
3. Start the container shell:
   - `docker compose up -d`
   - `docker compose exec app bash`
4. Inside the container, run `npm run start`
5. Open [http://localhost:5173](http://localhost:5173)

The frontend talks to the backend on `http://localhost:8002`.

## Local Development Without Containers

Containers are the preferred workshop path. If you want to run locally instead:
- Python 3.11+
- Node.js 22+
- `uv`

Then run:
```bash
cp .env.template .env
npm install
npm run start
```

## What Changed For IIT BHU
- removed the hosted OpenAI vector-store dependency from the core path
- removed Notion from the workshop-critical MCP flow
- replaced it with a local filesystem MCP demo
- reduced required setup to mainly Docker plus `OPENAI_API_KEY`
- made upload summaries explicit so they can be shown and discussed during the workshop

## Key Paths
- Backend agent wiring: `backend/app/agents_sdk/`
- Local retrieval and ingestion: `backend/app/services/vector_store_service.py`
- Document summaries: `backend/app/services/document_summarizer.py`
- Frontend app: `frontend/src/`
- Workshop sample documents: `resources/documents/`
- MCP-created notes: `workshop_notes/`

## Workshop Flow
1. Upload a few notes from `resources/documents/` or your own material.
2. Ask the agent to summarize or explain a topic from the uploaded notes.
3. Ask for a comparison or concept explanation with citations.
4. Ask the MCP notes agent to save a revision sheet as markdown.

## Notes
- Indexed data and uploaded files are stored locally in `data/`.
- Generated markdown notes are stored in `workshop_notes/`.
- Logfire is optional and disabled unless `LOGFIRE_TOKEN` is set.
