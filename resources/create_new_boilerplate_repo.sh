#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_REPO="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_TARGET="/Users/nagrawal/PycharmProjects/study_assistant_ai_boilerplate"
TARGET_DIR="${1:-$DEFAULT_TARGET}"

if [[ -e "$TARGET_DIR" ]]; then
  echo "Target already exists: $TARGET_DIR" >&2
  exit 1
fi

echo "Creating boilerplate repo at: $TARGET_DIR"

mkdir -p "$TARGET_DIR"
mkdir -p \
  "$TARGET_DIR/backend/app/agents_sdk" \
  "$TARGET_DIR/backend/app/models" \
  "$TARGET_DIR/backend/app/routers" \
  "$TARGET_DIR/backend/app/services" \
  "$TARGET_DIR/frontend/src" \
  "$TARGET_DIR/.devcontainer"

cp -R "$SOURCE_REPO/resources" "$TARGET_DIR/resources"

cat > "$TARGET_DIR/README.md" <<'EOF'
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
./workshop/init_env.sh
npm run setup
npm run start
```
EOF

cat > "$TARGET_DIR/.env.template" <<'EOF'
OPENAI_API_KEY=
OPENAI_DEFAULT_MODEL=gpt-4o-mini
APP_DATA_DIR=./data
APP_NOTES_DIR=./workshop_notes
LOG_LEVEL=INFO
LOGFIRE_TOKEN=
EOF

cat > "$TARGET_DIR/.nvmrc" <<'EOF'
22
EOF

cat > "$TARGET_DIR/.gitignore" <<'EOF'
.env
.venv/
node_modules/
frontend/node_modules/
dist/
frontend/dist/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
.idea/
.cursor/
data/
workshop_notes/
EOF

cat > "$TARGET_DIR/pyproject.toml" <<'EOF'
[project]
name = "study-assistant-ai-boilerplate"
version = "0.1.0"
description = "Workshop-friendly AI study assistant boilerplate"
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "openai",
    "openai-chatkit",
    "python-dotenv",
    "pypdf",
    "python-docx",
    "logfire",
    "logfire[fastapi]",
    "pytest",
    "pytest-asyncio",
    "pre-commit",
]

[project.optional-dependencies]
dev = [
    "ruff",
    "mypy",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["backend"]
EOF

cat > "$TARGET_DIR/package.json" <<'EOF'
{
  "name": "study-assistant-ai-boilerplate",
  "private": true,
  "scripts": {
    "setup": "npm install && npm --prefix frontend install && uv sync",
    "start": "node workshop/start.mjs",
    "frontend": "npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173",
    "backend": "uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8002"
  }
}
EOF

cat > "$TARGET_DIR/Dockerfile" <<'EOF'
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
EOF

cat > "$TARGET_DIR/.dockerignore" <<'EOF'
.git
.cursor
.idea
.venv
node_modules
frontend/node_modules
dist
data
workshop_notes
__pycache__
*.pyc
EOF

cat > "$TARGET_DIR/docker-compose.yml" <<'EOF'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    working_dir: /workspace
    command: sleep infinity
    ports:
      - "5173:5173"
      - "8002:8002"
    environment:
      CHOKIDAR_USEPOLLING: "true"
      WATCHPACK_POLLING: "true"
      UV_CACHE_DIR: "/home/vscode/.cache/uv"
    volumes:
      - .:/workspace
      - root_node_modules:/workspace/node_modules
      - frontend_node_modules:/workspace/frontend/node_modules
      - uv_cache:/home/vscode/.cache/uv

volumes:
  root_node_modules:
  frontend_node_modules:
  uv_cache:
EOF

cat > "$TARGET_DIR/.devcontainer/devcontainer.json" <<'EOF'
{
  "name": "study-assistant-ai-boilerplate",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",
  "remoteUser": "vscode",
  "shutdownAction": "stopCompose",
  "forwardPorts": [5173, 8002],
  "postCreateCommand": "bash ./workshop/bootstrap_workspace.sh && npm run setup",
  "postStartCommand": "bash ./workshop/bootstrap_workspace.sh",
  "customizations": {
    "vscode": {
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash"
      },
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint"
      ]
    }
  }
}
EOF

cat > "$TARGET_DIR/.pre-commit-config.yaml" <<'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.2
    hooks:
      - id: ruff-check
        args: [--fix, --unsafe-fixes]
      - id: ruff-format
EOF

cat > "$TARGET_DIR/ruff.toml" <<'EOF'
line-length = 120
target-version = "py311"

include = [
    "backend/app/**/*.py",
    "resources/**/*.py",
]

[format]
quote-style = "double"

[lint]
select = ["E", "F", "I", "W", "UP", "ASYNC", "B", "RUF", "FAST"]
ignore = ["E501"]
fixable = ["ALL"]
EOF

cat > "$TARGET_DIR/backend/app/main.py" <<'EOF'
from __future__ import annotations

from fastapi import FastAPI


app = FastAPI(title="Study Assistant AI Boilerplate")


@app.get("/exam-assistant/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
EOF

cat > "$TARGET_DIR/frontend/package.json" <<'EOF'
{
  "name": "study-assistant-ai-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "engines": {
    "node": ">=18.18",
    "npm": ">=9"
  },
  "dependencies": {
    "@openai/chatkit-react": "^0",
    "clsx": "^2.1.1",
    "lucide-react": "^0.544.0",
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  },
  "devDependencies": {
    "@eslint/js": "^8.57.1",
    "@types/node": "^24.5.2",
    "@types/react": "^19.2.0",
    "@types/react-dom": "^19.2.0",
    "@typescript-eslint/eslint-plugin": "^7.18.0",
    "@typescript-eslint/parser": "^7.18.0",
    "@vitejs/plugin-react-swc": "^3.5.0",
    "autoprefixer": "^10.4.20",
    "eslint": "^8.57.1",
    "eslint-config-prettier": "^9.1.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.7",
    "globals": "^15.3.0",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.13",
    "typescript": "^5.4.0",
    "vite": "^7.1.9",
    "vitest": "^3.2.4"
  }
}
EOF

cat > "$TARGET_DIR/frontend/tsconfig.json" <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "moduleDetection": "force",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "jsx": "react-jsx"
  },
  "include": ["src", "src/types"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

cat > "$TARGET_DIR/frontend/tsconfig.node.json" <<'EOF'
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
EOF

cat > "$TARGET_DIR/frontend/index.html" <<'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Study Assistant AI Boilerplate</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

cat > "$TARGET_DIR/frontend/vite.config.ts" <<'EOF'
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

const backendTarget = process.env.BACKEND_URL ?? "http://127.0.0.1:8002";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/exam-assistant": {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
});
EOF

cat > "$TARGET_DIR/frontend/src/main.tsx" <<'EOF'
import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>Study Assistant AI Boilerplate</h1>
      <p>Use the docs in resources/ to implement the full app.</p>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
EOF

cat > "$TARGET_DIR/workshop/bootstrap_workspace.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UV_CACHE_DIR="${UV_CACHE_DIR:-$HOME/.cache/uv}"

ensure_writable_dir() {
    local dir="$1"

    mkdir -p "$dir"

    if [[ -w "$dir" ]]; then
        return 0
    fi

    if command -v sudo >/dev/null 2>&1; then
        sudo chown -R "$(id -u):$(id -g)" "$dir"
    else
        chown -R "$(id -u):$(id -g)" "$dir" 2>/dev/null || true
    fi

    if [[ ! -w "$dir" ]]; then
        echo "Directory is not writable: $dir" >&2
        exit 1
    fi
}

ensure_writable_dir "$PROJECT_DIR/node_modules"
ensure_writable_dir "$PROJECT_DIR/frontend/node_modules"
ensure_writable_dir "$UV_CACHE_DIR"
EOF

cat > "$TARGET_DIR/workshop/start.mjs" <<'EOF'
import { spawn } from "node:child_process";

const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";

function prefixStream(stream, label) {
  let buffer = "";

  stream.on("data", (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      process.stdout.write(`[${label}] ${line}\n`);
    }
  });

  stream.on("end", () => {
    if (buffer.length > 0) {
      process.stdout.write(`[${label}] ${buffer}\n`);
    }
  });
}

function startProcess(label, script) {
  const child = spawn(npmCommand, ["run", script], {
    stdio: ["inherit", "pipe", "pipe"],
    env: process.env,
  });

  prefixStream(child.stdout, label);
  prefixStream(child.stderr, label);
  return child;
}

const children = [
  { label: "backend", child: startProcess("backend", "backend") },
  { label: "frontend", child: startProcess("frontend", "frontend") },
];

let shuttingDown = false;

function stopChildren(signal = "SIGTERM") {
  if (shuttingDown) return;
  shuttingDown = true;

  for (const { child } of children) {
    if (!child.killed) {
      child.kill(signal);
    }
  }
}

for (const { label, child } of children) {
  child.on("exit", (code, signal) => {
    if (!shuttingDown) {
      stopChildren();
      if (signal) {
        console.error(`[${label}] exited due to signal ${signal}`);
        process.exit(1);
      }
      process.exit(code ?? 1);
    }
  });
}

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => {
    stopChildren(signal);
    process.exit(0);
  });
}
EOF

git -C "$TARGET_DIR" init
git -C "$TARGET_DIR" branch -m main

echo
echo "Initialized new git repo:"
echo "  $TARGET_DIR"
echo
echo "Next steps:"
echo "  cd \"$TARGET_DIR\""
echo "  ./workshop/init_env.sh"
echo "  npm run setup"
echo "  npm run start"
echo "  git status"
