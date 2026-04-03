# Study Assistant AI Boilerplate

This repository is a fresh scaffold for a workshop-friendly AI study assistant built with FastAPI, React, OpenAI Agents SDK, local RAG, and MCP filesystem tools.

## Start Here

- Implementation spec: `resources/BOILERPLATE_IMPLEMENTATION_SPEC.md`
- LLM build prompt: `resources/BOILERPLATE_LLM_PROMPT.md`
- Workshop presentation: `resources/AGENTS_PRESENTATION.md`

## Current Status

This repo is intentionally scaffolded but not fully implemented yet. It is designed to be handed to an LLM or developer to build out using the docs in `resources/`.

## Intended Stack

- Python 3.11+
- `uv`
- FastAPI
- OpenAI Agents SDK
- React + TypeScript + Vite
- Docker + devcontainer
- `ruff`, `pytest`, `mypy`, `pre-commit`
- optional `logfire`

## Quick Start

```bash
cp .env.template .env
uv sync
npm install
npm run start
```
