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

## What You Should Install Before the Workshop

Please complete setup before the session if possible.

Required:
- Git
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- One IDE: VS Code, Cursor, or PyCharm

Recommended setup path:
- Use the devcontainer workflow. This gives you Python, Node.js, and uv inside the container and avoids most machine-specific issues.

Windows note:
- If you use Docker Desktop on Windows, make sure WSL 2 is installed and Docker Desktop is using the WSL 2 backend.

## Install Links

- Git: <https://git-scm.com/>
- Docker Desktop: <https://www.docker.com/products/docker-desktop/>
- Docker Engine (Linux): <https://docs.docker.com/engine/install/>
- Install WSL: <https://learn.microsoft.com/windows/wsl/install>
- VS Code: <https://code.visualstudio.com/>
- Cursor: <https://www.cursor.com/>
- PyCharm: <https://www.jetbrains.com/pycharm/download/>
- Dev Containers extension: <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers>

## Before You Arrive

Repository for the workshop:
- <https://github.com/regalmoix/Exam-Preparation-AI-Agent/tree/bhu>

Please make sure you are on the `bhu` branch.

Recommended clone command:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
```

If you already cloned the repo in some other way, run:

```bash
git fetch origin
git checkout bhu
```

After cloning, use `README.md` in the repo as the main setup guide for the workshop.

Then:

1. Confirm Docker starts successfully.
2. Confirm `docker compose version` works.
3. Open the repo in your IDE.
4. If using VS Code or Cursor, make sure the Dev Containers extension is installed.

If you want to sanity-check your machine, run:

- macOS/Linux: `./workshop/preflight.sh`
- Windows PowerShell: `powershell -ExecutionPolicy Bypass -File .\workshop\preflight.ps1`

PowerShell note:
- If Windows blocks PowerShell scripts, run `Set-ExecutionPolicy -Scope Process Bypass` in that PowerShell window and retry.

## What “Ready” Looks Like

You are workshop-ready if:
- the repository is cloned locally
- you are on the `bhu` branch
- Docker starts successfully
- `docker compose version` works
- your IDE is installed and can open the repo
- if using VS Code or Cursor, the Dev Containers extension is installed
- on Windows, WSL 2 is installed and Docker Desktop is using the WSL 2 backend

## OpenAI API Key

Do not worry about bringing an OpenAI API key in advance.

An API key will be provided on the day of the workshop, so your main job beforehand is just to get Docker, your IDE, and the repository setup working.

## Goal By The End

By the end of the workshop, you should be able to understand how modern agent systems are structured and build or extend a multi-agent study assistant that can answer questions over documents and save revision notes locally.
