# Pre-Workshop Brief

## Building AI Agents: From LLMs to Multi-Agent Systems

This workshop is a hands-on introduction to building practical AI agent systems using the OpenAI API, the OpenAI Agents SDK, FastAPI, React, local retrieval, and MCP.

## What We Will Cover

- LLM basics and chat completions
- Multi-turn conversations and memory
- Tool calling and structured outputs
- Agents and multi-agent handoffs
- Local RAG over uploaded study material
- MCP-based note generation
- A full study assistant app with backend + frontend

## Workshop Format

- Short concept explanations
- Live walkthrough of progressively richer code examples
- Hands-on coding checkpoints in a working app
- End-to-end demo of upload, Q&A, and revision-note generation

## Recommended Background

You do not need prior agent-building experience.

Helpful prerequisites:
- basic Python (ability to read and understand, if not ability to write)
- basic JavaScript or TypeScript familiarity (optional, backend focused)
- comfort using the terminal
- basic Git usage
- basic understanding of APIs or web apps

---

## Setup Path: GitHub Codespaces via VS Code (Preferred)

This is the recommended setup for all students. It gives everyone the same Linux dev environment running on GitHub's cloud, with ports forwarded to your local machine so the app works on `localhost`.

**Why this path?**
- No Docker, Python, Node.js, or `uv` installation needed on your machine
- Everyone gets the same environment regardless of OS
- The ChatKit UI component only works on `localhost`, and VS Code automatically forwards Codespace ports to your local `localhost`

### What You Need to Install

1. **VS Code** (free): <https://code.visualstudio.com/>

2. **GitHub Codespaces extension** for VS Code:
   <https://marketplace.visualstudio.com/items?itemName=GitHub.codespaces>

3. **A GitHub account** (free): <https://github.com/signup>

That's it. No Docker, no Python, no Node.js needed on your machine.

### Step-by-Step Setup

#### 1. Sign in to GitHub from VS Code

Open VS Code and sign in to your GitHub account:
- Click the **Accounts** icon in the bottom-left of the VS Code sidebar (person icon)
- Click **Sign in with GitHub**
- Complete the browser-based authentication flow
- Once signed in, you should see your GitHub username in the Accounts menu

This is required for the Codespaces extension to work.

#### 2. Fork the repository on the `bhu` branch

1. Open the repository in your browser: <https://github.com/regalmoix/Exam-Preparation-AI-Agent/tree/bhu>
2. Make sure you are viewing the **`bhu`** branch (check the branch dropdown)
3. Click **Fork** (top-right of the page)
4. In the fork dialog, **uncheck** "Copy the `main` branch only" so you get the `bhu` branch
5. Click **Create fork**
6. On your fork's page, switch to the **`bhu`** branch and confirm the code is there

#### 3. Create a Codespace from VS Code

1. Open VS Code
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
3. Type **"Codespaces: Create New Codespace"** and select it
4. Select your fork of the repository (e.g. `your-username/Exam-Preparation-AI-Agent`)
5. Select the **`bhu`** branch
6. Choose the default machine type (2-core is fine)
7. Wait for the Codespace to build (first time takes 2-3 minutes)

VS Code will reopen connected to the Codespace. You will see `[Codespaces]` in the bottom-left corner.

#### 4. Configure your API key

In the VS Code terminal (inside the Codespace):

```bash
./workshop/init_env.sh
```

Edit `.env` and add the OpenAI API key (one will be provided during the workshop):

```
OPENAI_API_KEY=sk-proj-...
```

#### 5. Start the app

```bash
npm run start
```

This starts the FastAPI backend on port **8002** and the Vite frontend on port **5173**.

VS Code will automatically detect the forwarded ports. When it asks to open in browser, click **Open in Browser** for port 5173, or simply navigate to:

```
http://localhost:5173
```

The port forwarding happens automatically — `localhost:5173` on your machine connects to port 5173 inside the Codespace.

#### 6. Verify it works

1. Open `http://localhost:5173` in your browser
2. You should see the Study Assistant with a two-panel layout
3. Upload `resources/documents/CPU.md` using the left panel
4. Ask a question like "What is an instruction pointer?"
5. If you get a response grounded in the CPU document, you are ready

Optional health check from the Codespace terminal:

```bash
./workshop/healthcheck.sh
```

### Important: Why VS Code + Codespaces (Not Browser)

The ChatKit web component that powers the chat panel loads from `cdn.platform.openai.com` and only works when the app is served from `localhost`. If you open the Codespace directly in a browser (the GitHub-provided URL like `*.github.dev`), the chat panel will not render.

By connecting to the Codespace from VS Code on your local machine, VS Code forwards the ports so the app appears at `http://localhost:5173` on your machine, and ChatKit works correctly.

---

## Alternative: Local Setup (Without Codespaces)

If you prefer running directly on your machine without Codespaces, you need to install the following:

### Prerequisites

- Python 3.11+
- Node.js 22 (`.nvmrc` is pinned to `22`)
- npm 9+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

### Steps

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent
./workshop/init_env.sh
# Edit .env → add OPENAI_API_KEY
npm run setup
npm run start
```

Open `http://localhost:5173`.

### Preflight Check

Run the preflight script to verify your local machine has everything:

- macOS/Linux: `./workshop/preflight.sh`
- Windows PowerShell: `powershell -ExecutionPolicy Bypass -File .\workshop\preflight.ps1`

---

## What "Ready" Looks Like

You are workshop-ready if:

- **Codespaces path**: VS Code is connected to your Codespace, `npm run start` works, and `http://localhost:5173` shows the Study Assistant in your browser
- **Local path**: all prerequisites are installed, `npm run start` works, and `http://localhost:5173` loads the app

## OpenAI API Key

Do not worry about bringing an OpenAI API key in advance.

An API key will be provided on the day of the workshop. Your main job beforehand is just to get VS Code, the Codespaces extension, and a GitHub account ready.

## Goal By The End

By the end of the workshop, you should be able to understand how modern agent systems are structured and build or extend a multi-agent study assistant that can answer questions over documents and save revision notes locally.
