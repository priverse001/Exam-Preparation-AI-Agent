# Boilerplate Build Prompt For An LLM

Use this prompt to ask another LLM or coding agent to build a fresh repository from scratch.

---

Build a workshop-friendly monorepo for an AI study assistant web app.

## Goal

Create a local-first study assistant where users can upload study materials, ask grounded questions about them, and create markdown revision notes using an MCP filesystem agent.

## Product Requirements

- Users can upload `pdf`, `txt`, `md`, `html`, `docx`, and `json` files.
- Uploaded files are stored locally.
- Backend extracts text from uploaded files.
- Backend generates a short summary and description for each uploaded file using OpenAI.
- Backend chunks and indexes extracted text locally.
- Users can ask questions in a chat UI.
- Agent answers must be grounded only in uploaded material.
- Factual claims must include citations using filename and section labels.
- Users can ask the system to create revision notes.
- A notes agent writes markdown files to a local notes directory through MCP filesystem tools.

## Architecture Requirements

- Monorepo structure with `backend/`, `frontend/`, and `resources/`.
- Python FastAPI backend.
- React + TypeScript frontend using Vite.
- OpenAI Agents SDK for agents, tools, handoffs, and sessions.
- ChatKit-based streaming chat UI.
- Filesystem MCP server for notes creation.
- Root-level `pyproject.toml` and root-level `uv.lock`.
- Root `.venv` should be the expected Python environment.
- Docker/devcontainer support is required.
- Include project tooling and config from day one: `pre-commit`, `ruff`, `.nvmrc`, `.env.template`, Docker, `docker-compose.yml`, `.devcontainer/devcontainer.json`, and optional `logfire`.
- Copy the `resources/` directory structure as-is, including workshop documents and code examples.

## Required Repo Layout

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

## Backend Requirements

Expose the backend under `/exam-assistant`.

Required endpoints:

- `POST /exam-assistant/chatkit`
- `GET /exam-assistant/health`
- `GET /exam-assistant/documents`
- `POST /exam-assistant/documents/upload`
- `GET /exam-assistant/documents/{id}`
- `GET /exam-assistant/documents/{id}/file`
- `DELETE /exam-assistant/documents/{id}`

### Document ingestion requirements

- Validate supported file extensions.
- Save uploaded originals locally.
- Extract text from each supported file type.
- Generate a short `description` and `summary`.
- Create overlapping chunks for retrieval.
- Persist chunk index locally, for example in JSON.
- Persist document metadata locally.

### Retrieval requirements

- Implement a simple local retrieval layer.
- A full embedding/vector database is not required.
- Search should return top matching excerpts with:
  - file id
  - filename
  - section label or citation
  - excerpt text
  - basic relevance score

## Agent Requirements

Create these three agents:

1. `TriageAgent`
2. `CourseMaterialAgent`
3. `RevisionNotesAgent`

### `TriageAgent`

- Routes content questions, summaries, and explanations to `CourseMaterialAgent`.
- Routes save/export/create-notes requests to `RevisionNotesAgent`.
- Keeps internal handoffs invisible unless explicitly asked.

### `CourseMaterialAgent`

- Uses only uploaded materials as the source of truth.
- Uses retrieval tools before answering.
- Explains concepts clearly for students.
- Cites every factual statement.
- If material is missing, says so honestly and asks for more uploads.

Tools:

- `search_uploaded_materials`
- `list_uploaded_materials`

### `RevisionNotesAgent`

- Creates markdown revision notes.
- Uses retrieved material when note content depends on uploaded documents.
- Writes only inside the allowed notes directory.
- Mentions the created or updated filename in the response.

Tools:

- `search_uploaded_materials`
- `list_uploaded_materials`
- MCP filesystem tools

## MCP Requirements

- Use the filesystem MCP server.
- Scope it to a single notes directory such as `workshop_notes/`.
- Do not rely on Notion or other SaaS integrations for the main workshop flow.

## Prompting Requirements

Use strong, explicit prompts.

Each agent prompt should include:

- role
- workflow
- tool rules
- edge-case handling
- response format

Important prompt rules:

- ALWAYS retrieve before content answers.
- NEVER invent facts.
- ALWAYS cite sources for factual claims.
- If no uploaded material exists, ask the user to upload documents first.
- Notes agent must NEVER write outside the notes directory.

## Frontend Requirements

Build a clean workshop-oriented UI with:

- chat panel
- uploaded documents panel
- upload area
- preview modal
- delete document action
- starter prompts
- optional dark/light theme

Frontend behavior:

- fetch documents on load
- refresh document list after upload or delete
- connect chat UI to backend streaming endpoint

## Tooling Requirements

### Python

- Use `uv`
- Root-level `pyproject.toml`
- Root-level `uv.lock`
- Root `.venv`
- Configure `ruff`, `mypy`, `pytest`, and `pre-commit`
- Include a `.pre-commit-config.yaml`
- Include a `ruff.toml`

### JavaScript

- Root `package.json`
- Root `npm run start` should run backend and frontend together
- Include `.nvmrc` targeting Node.js 22

### Containers and editor support

- Include a `Dockerfile`
- Include `docker-compose.yml`
- Include `.devcontainer/devcontainer.json`
- The devcontainer should install Node.js, Python tooling, `uv`, and run dependency install commands automatically

## Environment Variables

Support:

- `OPENAI_API_KEY`
- optional `OPENAI_DEFAULT_MODEL`
- optional `APP_DATA_DIR`
- optional `APP_NOTES_DIR`
- optional `LOGFIRE_TOKEN`
- optional `LOG_LEVEL`

Provide `.env.template`.

## Logging and observability

- Include optional `logfire` integration on the backend
- It must be safe to run without `LOGFIRE_TOKEN`
- Add clear comments or docs explaining that tracing is optional for the workshop

## Workshop Checkpoints

Implement in this order:

1. Repo scaffold and local run scripts
2. Basic chat completion example
3. Multi-turn memory example
4. First tool-calling example
5. Structured output example
6. Single-agent study assistant
7. Multi-agent routing with handoffs
8. Real document upload and ingestion
9. Local RAG over uploaded material
10. MCP filesystem notes agent
11. Full frontend + backend integration
12. Setup docs and workshop polish

## Non-Goals

Do not spend time on:

- authentication
- user accounts
- production-grade vector search
- cloud storage
- enterprise permissions
- complex deployment infrastructure

## Acceptance Criteria

The project is complete when:

1. `uv sync` works from repo root.
2. `npm install` works.
3. `npm run start` runs backend and frontend together.
4. Users can upload supported files.
5. Uploaded files are summarized and indexed locally.
6. Chat answers are grounded and cited.
7. Notes can be created as markdown through MCP.
8. The repo is clean and teachable for a workshop.
9. The repo includes working dev tooling: `pre-commit`, `ruff`, `.nvmrc`, Docker, and devcontainer config.
10. The `resources/` directory is present with workshop documents and example scripts.

## Implementation Style

- Prefer simple local-first solutions over external services.
- Keep code readable and educational.
- Favor explicit structure over abstraction-heavy code.
- Add comments only where they materially help workshop participants.
- Keep the repo suitable as both a teaching reference and a starting boilerplate.

---

If useful, also generate:

- `README.md`
- sample documents in `resources/documents/`
- basic example scripts in `resources/code_examples/`
- `.pre-commit-config.yaml`
- `ruff.toml`
- `.nvmrc`
- `.devcontainer/devcontainer.json`
