# Study Assistant AI

An AI-powered study assistant that lets students upload course materials and chat with an intelligent multi-agent system. Built as a teaching demo for the **"Building AI Agents: From LLMs to Multi-Agent Systems"** workshop at BHU.

## Who Should Read What

If you are a student or workshop participant:
- use `README.md` as the full setup and workshop guide

If you are conducting the workshop:
- use `resources/DEMO_PLAYBOOK.md` as the instructor runbook
- use `resources/AGENTS_PRESENTATION.md` for slides
- use `resources/code_examples/` as the progressive teaching examples
- use `resources/documents/` as sample upload files for demos and testing

## What's Inside

- **FastAPI backend** with a multi-agent pipeline (Triage → CourseMaterial / RevisionNotes) powered by the OpenAI Agents SDK.
- **Local RAG** — upload PDF, Markdown, DOCX, HTML, TXT, or JSON documents; content is chunked and keyword-searched at query time with source citations.
- **MCP integration** — the RevisionNotes agent uses the `@modelcontextprotocol/server-filesystem` to save study notes to disk.
- **ChatKit frontend** — React + TypeScript UI with a document sidebar, file preview, dark/light theme, and streaming chat via the ChatKit web component.
- **Structured outputs** — Pydantic models for typed tool responses (e.g. `TopicSummary`).
- **Optional Logfire tracing** — instrument both FastAPI and the Agents SDK for full observability.

### Architecture

```
                 ┌──────────────────┐
                 │   Triage Agent   │
                 └────────┬─────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
  ┌─────────▼───────────┐    ┌──────────▼──────────┐
  │ CourseMaterialAgent │    │ RevisionNotesAgent  │
  │  (Q&A from docs)    │    │  (Create & save     │
  │                     │    │   notes via MCP)    │
  └────────┬────────────┘    └──────────┬──────────┘
           │                            │
  ┌────────▼─────────┐         ┌────────▼─────────┐
  │ search_materials │         │ MCP Filesystem   │
  │ list_materials   │         │ (write_file,     │
  │ topic_summary    │         │  list_directory) │
  └──────────────────┘         └──────────────────┘
```

---

## Getting Started (Devcontainer — Recommended)

The devcontainer gives you a fully configured environment with Python 3.11, Node.js 22, and `uv` pre-installed. It works identically on **Windows, macOS, and Linux**.

Recommended editors for the workshop:
- `VS Code` + Dev Containers
- `Cursor` + Dev Containers
- `PyCharm` + Dev Containers

Also supported:
- any editor using the generic local setup path later in this README

### Before Class

Install these before the workshop starts:

1. Docker Desktop
2. Git
3. One editor: `VS Code`, `Cursor`, or `PyCharm`
4. An OpenAI API key
5. This repository cloned locally

### Helper Scripts

These scripts are meant to reduce setup trouble:

- `./workshop/preflight.sh`
- `powershell -ExecutionPolicy Bypass -File .\workshop\preflight.ps1`
- `./workshop/init_env.sh`
- `powershell -ExecutionPolicy Bypass -File .\workshop\init_env.ps1`
- `./workshop/healthcheck.sh`
- `powershell -ExecutionPolicy Bypass -File .\workshop\healthcheck.ps1`

Windows PowerShell note:

- On some student machines, PowerShell script execution is blocked by policy.
- For this workshop, use the commands above exactly as written with `powershell -ExecutionPolicy Bypass -File ...`.
- Do not rely on running `.\workshop\preflight.ps1` directly unless your machine already allows local script execution.
- If PowerShell still blocks script execution, open a fresh PowerShell window and run:
  ```powershell
  Set-ExecutionPolicy -Scope Process Bypass
  ```
  Then rerun the workshop script command in that same window.
- Microsoft guide: [about_Execution_Policies](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_execution_policies)

What the preflight scripts validate:

- required for the recommended devcontainer path: `git`, `docker`, Docker daemon access, and `docker compose`
- optional but required for the local path: Python `3.11+`, Node.js `22`, `npm 9+`, and `uv`
- whether `.env` exists and whether `OPENAI_API_KEY` is populated

Recommended usage:

1. Run the preflight script before class.
2. Use the env-init script instead of manually copying `.env.template`.
3. After `npm run start`, run the healthcheck script to confirm the app is reachable.

### Step 0: Install prerequisites on your machine

For the recommended devcontainer path, you need Git, Docker, Docker Compose support, and an editor on your host OS. Everything else runs inside the container.

| Software | Why | Install | Guide |
|----------|-----|---------|-------|
| **Git** | Clone the repository | [git-scm.com](https://git-scm.com/) | [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) |
| **Docker Desktop / Docker Engine** | Runs the devcontainer | [docker.com/get-started](https://www.docker.com/get-started/) — Windows/macOS/Linux. On Windows, enable **WSL 2 backend** during setup. | [Docker Desktop install](https://docs.docker.com/desktop/), [Docker Engine install](https://docs.docker.com/engine/install/) |
| **Docker Compose support** | Required because the devcontainer uses `docker-compose.yml` | Included with modern Docker Desktop and current Docker Engine installs as `docker compose` | [docker compose docs](https://docs.docker.com/compose/) |
| **VS Code, Cursor, or PyCharm** | Recommended editor for the workshop | [code.visualstudio.com](https://code.visualstudio.com/), [cursor.com](https://www.cursor.com/), or PyCharm | [VS Code](https://code.visualstudio.com/docs/setup/setup-overview), [Cursor](https://docs.cursor.com/get-started/installation), [PyCharm](https://www.jetbrains.com/help/pycharm/installation-guide.html) |
| **Dev Containers extension / IDE workflow** | Opens the project inside Docker | In VS Code or Cursor, install the Dev Containers extension (`ms-vscode-remote.remote-containers`). In PyCharm, use the IDE's devcontainer workflow. | [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), [PyCharm Dev Containers](https://www.jetbrains.com/help/pycharm/start-dev-container-inside-ide.html) |

> **Windows users**: Make sure Docker Desktop is running with the WSL 2 backend (Settings → General → "Use the WSL 2 based engine"). This is required for the Linux container to work. If WSL is not installed yet, follow [Install WSL](https://learn.microsoft.com/windows/wsl/install).

> **Linux users**: If you don't want Docker Desktop, install Docker Engine directly: [docs.docker.com/engine/install](https://docs.docker.com/engine/install/). Make sure your user is in the `docker` group (`sudo usermod -aG docker $USER`).

Quick host checks:

- Windows:
  ```powershell
  wsl --status
  docker --version
  docker compose version
  git --version
  ```
- macOS / Linux:
  ```bash
  docker --version
  docker compose version
  git --version
  ```

### Step 1: Clone and open

If you use `VS Code`:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent
code .
```

If you use `Cursor`:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent
cursor .
```

If you use `PyCharm`:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent
```

Then open the project in `PyCharm` and use the IDE's devcontainer workflow to reopen the project in the container.

When the editor opens, you'll see a prompt:

> **"Reopen in Container"** — click it.

Or manually: `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) → type **"Dev Containers: Reopen in Container"** → Enter.

The first build takes 2-3 minutes (downloads the Docker image, installs Node.js 22, `uv`, and all project dependencies). Subsequent opens are instant.

### Optional: Generate a local scaffold branch

The `bhu` branch is the canonical full solution. If you want students to work through checkpoint exercises, generate a local scaffold branch that starts fully working:

```bash
./workshop/create_scaffold_branch.sh
git switch workshop-scaffold
./workshop/workshop.sh status
```

This creates a local branch that is effectively `bhu + one local workshop commit`. Students can run the app end-to-end immediately, then strip one checkpoint at a time during the workshop. The workshop script restores checkpoints from the recorded solution commit with:

```bash
./workshop/workshop.sh solve 1
./workshop/workshop.sh reset
```

### Step 2: Configure your API key

Inside the container terminal (which opens automatically):

```bash
./workshop/init_env.sh
```

On Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\workshop\init_env.ps1
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-proj-...
```

> Get a key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys) if you don't have one.

### Step 3: Start the app

```bash
npm run start
```

This single command:
- Installs Python dependencies (`uv sync`)
- Installs frontend dependencies (`npm install`)
- Starts the FastAPI backend on port **8002**
- Starts the Vite dev server on port **5173**

Optional health check:

```bash
./workshop/healthcheck.sh
```

On Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\workshop\healthcheck.ps1
```

### Step 4: Open in browser

Navigate to **http://localhost:5173** on your host machine (ports are auto-forwarded by the devcontainer).

1. **Upload** a study document via the left panel (try `resources/documents/CPU.md`).
2. **Ask questions** — *"Explain the key concepts from my notes"*
3. **Create revision notes** — *"Create revision notes about CPU architecture and save them"*
4. Check the `workshop_notes/` folder for saved markdown files.

---

## Alternative: Local Setup (Without Devcontainer)

If you prefer running directly on your machine without Docker, follow this path.

### Prerequisites

- Python 3.11+
- Node.js 22 (`.nvmrc` is pinned to `22`)
- npm 9+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Git
- OpenAI API key

Install guides for local setup:

- Python: [python.org downloads](https://www.python.org/downloads/)
- Node.js: [Node.js downloads](https://nodejs.org/en/download) or [nvm-sh/nvm](https://github.com/nvm-sh/nvm)
- uv: [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

Quick local checks:

- macOS / Linux:
  ```bash
  python3 --version
  node --version
  npm --version
  uv --version
  ```
- Windows PowerShell:
  ```powershell
  python --version
  node --version
  npm --version
  uv --version
  ```

### Steps

macOS / Linux:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent

# Optional: generate a local scaffold branch for the exercises
# ./workshop/create_scaffold_branch.sh
# git switch workshop-scaffold

./workshop/init_env.sh
# Edit .env → add OPENAI_API_KEY

nvm install 22
nvm use 22
uv sync
npm install
npm run start
```

Open **http://localhost:5173**.

Optional health check:

```bash
./workshop/healthcheck.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent

powershell -ExecutionPolicy Bypass -File .\workshop\init_env.ps1
# Edit .env and add OPENAI_API_KEY

python --version
node --version
npm --version
uv --version
npm install
npm run start
```

On Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\workshop\healthcheck.ps1
```

### First Run Checklist

Once the app is running:

1. Open `http://localhost:5173`.
2. Upload `resources/documents/CPU.md`.
3. Ask: `What is an instruction pointer?`
4. Ask: `Create revision notes about CPU architecture and save them`.
5. Confirm a file appears in `workshop_notes/`.

If all of that works, your setup is ready.

### Workshop Exercise Flow

The workshop branch starts fully working. During the session, strip exactly one checkpoint at a time.

Useful commands:

```bash
./workshop/workshop.sh status
./workshop/workshop.sh checkpoint 1
./workshop/workshop.sh solve 1
./workshop/workshop.sh reset
```

How it works:
- `status` shows whether any checkpoint is currently active
- `checkpoint N` strips one exercise and prints which files to edit
- `solve N` restores the official solution for that checkpoint
- only one checkpoint can be active at a time

---

## Project Structure

```
├── backend/
│   └── app/
│       ├── agents_sdk/           # Agent definitions, tools, prompts, MCP
│       │   ├── agents.py         # TriageAgent, CourseMaterialAgent, RevisionNotesAgent
│       │   ├── prompts.py        # Structured agent instructions
│       │   ├── tools.py          # @function_tool definitions + TopicSummary model
│       │   └── mcp.py            # Filesystem MCP server connection
│       ├── models/               # Pydantic models (DocumentMetadata, SearchResult, etc.)
│       ├── routers/              # FastAPI routes (chat, documents)
│       ├── services/             # Business logic
│       │   ├── chat_server.py    # ChatKit server + streaming agent pipeline
│       │   ├── chat_store.py     # In-memory thread/item store
│       │   ├── document_store.py # Document upload, metadata, chunk persistence
│       │   ├── retrieval.py      # Keyword-based TF search over chunks
│       │   ├── extraction.py     # Text extraction (PDF, DOCX, etc.)
│       │   ├── chunking.py       # Word-based overlapping chunker
│       │   ├── summarize.py      # AI-powered document summarization
│       │   └── config.py         # Environment config
│       └── main.py               # FastAPI app + optional logfire setup
├── frontend/
│   └── src/
│       ├── App.tsx               # Two-panel layout (documents + chat)
│       ├── components/
│       │   ├── ChatPanel.tsx     # ChatKit web component wrapper
│       │   └── DocumentPanel.tsx # Upload, list, preview, delete documents
│       ├── api.ts                # API client functions
│       └── index.css             # Tailwind styles
├── resources/
│   ├── AGENTS_PRESENTATION.md    # Workshop slide deck (25 slides)
│   ├── code_examples/            # 8 progressive Python examples (basic chat → MCP)
│   └── documents/                # Sample study materials for testing
├── data/                         # Uploaded documents + metadata + chunks (gitignored)
├── workshop_notes/               # Saved revision notes via MCP (gitignored)
├── .devcontainer/                # VS Code devcontainer config
├── Dockerfile                    # Python 3.11 + Node 22 image
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/exam-assistant/health` | Health check |
| `POST` | `/exam-assistant/documents/upload` | Upload a document (multipart form) |
| `GET` | `/exam-assistant/documents` | List all documents |
| `GET` | `/exam-assistant/documents/{id}` | Get document metadata |
| `GET` | `/exam-assistant/documents/{id}/file` | Download original file |
| `DELETE` | `/exam-assistant/documents/{id}` | Delete a document |
| `POST` | `/exam-assistant/chatkit` | ChatKit streaming endpoint (SSE) |

## Workshop Concepts Demonstrated

This app is a complete working example for the workshop presentation (`resources/AGENTS_PRESENTATION.md`). Every core concept is implemented:

| Concept | Where in Code |
|---------|--------------|
| LLM / Chat Completion | Every agent call → OpenAI API |
| Multi-turn conversations | `chat_store.py` thread history |
| AI Agents | 3 autonomous agents in `agents.py` |
| Tools / Function Calling | `@function_tool` in `tools.py` |
| Structured Outputs | `TopicSummary` Pydantic model in `tools.py` |
| Agents SDK | `Agent`, `Runner.run_streamed`, `function_tool` |
| Multi-agent + Handoffs | Triage → CourseMaterial / RevisionNotes |
| Sessions | ChatKit thread management |
| Tracing (Logfire) | `logfire.instrument_openai_agents()` in `main.py` |
| RAG | Upload → chunk → keyword search → cite sources |
| Prompting best practices | Structured prompts with `## sections`, `MUST`/`NEVER` rules |
| MCP | Filesystem MCP server for saving notes |
| Streaming | `Runner.run_streamed` + SSE to ChatKit |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_DEFAULT_MODEL` | `gpt-4o-mini` | Model for all agents |
| `APP_DATA_DIR` | `./data` | Storage for uploads, metadata, chunks |
| `APP_NOTES_DIR` | `./workshop_notes` | Directory for MCP-saved revision notes |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `LOGFIRE_TOKEN` | *(empty)* | Set to enable Logfire tracing |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `npm run start` fails with Node errors | Make sure Node 22+ is active: `node -v`. In devcontainer this is automatic. |
| Chat panel is blank | The ChatKit CDN script must load. Check your internet connection — the component loads from `cdn.platform.openai.com`. |
| "Please upload study materials first" | Upload a document before asking content questions. Try `resources/documents/CPU.md`. |
| Revision notes fail on first try | The MCP filesystem server needs a moment to connect on cold start. Retry the message. |
| Port 5173/8002 already in use | Kill existing processes: `lsof -ti :5173 \| xargs kill` (or change ports in `package.json`). |
| Docker build fails on Windows | Ensure WSL 2 backend is enabled in Docker Desktop settings. |

## Customization

- **Add a new agent**: Define it in `agents.py`, write a prompt in `prompts.py`, add tools, and include it in the triage agent's `handoffs` list.
- **Add a new tool**: Use `@function_tool` in `tools.py` and add it to the relevant agent's `tools` list.
- **Change the knowledge base**: Upload different documents through the UI or API.
- **Switch models**: Set `OPENAI_DEFAULT_MODEL` in `.env` (e.g. `gpt-4o` for higher quality).
- **Add MCP servers**: Connect additional MCP servers in `mcp.py` and assign them to agents.
