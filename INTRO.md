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

## Recommended Setup Path

Preferred setup for students:
- Use **GitHub Codespaces** on your own fork of the repository.
- This gives everyone the same Linux dev environment and removes almost all local machine dependency issues.

Fallback setup:
- If you do not want to use Codespaces, use the local devcontainer workflow with Docker.

## What You Should Install Before the Workshop

For the preferred Codespaces path, you only need:
- a GitHub account
- access to GitHub Codespaces
- a modern browser

For the fallback local devcontainer path, you need:
- Git
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- One IDE: VS Code, Cursor, or PyCharm

Windows note for the fallback local path:
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

Preferred Codespaces preparation:

1. Open the repository page and switch to the `bhu` branch.
2. Fork the repository while you are viewing the `bhu` branch.
3. Open your fork and confirm the branch is still `bhu`.
4. Create a new Codespace from that branch.
5. In the Codespace terminal, use `README.md` as the main setup guide.

Fallback local preparation:

1. Clone the repository on the `bhu` branch.
2. Confirm Docker starts successfully.
3. Confirm `docker compose version` works.
4. Open the repo in your IDE.
5. If using VS Code or Cursor, make sure the Dev Containers extension is installed.

Fallback local clone command:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
```

If you want to sanity-check your machine for the fallback local path, run:

- macOS/Linux: `./workshop/preflight.sh`
- Windows PowerShell: `powershell -ExecutionPolicy Bypass -File .\workshop\preflight.ps1`

PowerShell note for the fallback local path:
- If Windows blocks PowerShell scripts, run `Set-ExecutionPolicy -Scope Process Bypass` in that PowerShell window and retry.

## What “Ready” Looks Like

You are workshop-ready if:
- for Codespaces: you have a fork, your Codespace is created from the `bhu` branch, and the repo opens successfully in the browser
- for the fallback local path: the repository is cloned locally on `bhu`, Docker starts successfully, and your IDE can reopen the repo in the devcontainer

## OpenAI API Key

Do not worry about bringing an OpenAI API key in advance.

An API key will be provided on the day of the workshop, so your main job beforehand is just to get Docker, your IDE, and the repository setup working.

## Goal By The End

By the end of the workshop, you should be able to understand how modern agent systems are structured and build or extend a multi-agent study assistant that can answer questions over documents and save revision notes locally.
