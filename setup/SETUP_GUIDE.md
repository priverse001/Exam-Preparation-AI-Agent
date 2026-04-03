# IIT BHU AI Workshop - Setup Guide

## Prerequisites

You only need two things installed before the workshop:

1. **Docker Desktop** (or any Docker-compatible runtime with `docker compose`)
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - macOS: https://docs.docker.com/desktop/install/mac-install/
   - Linux: https://docs.docker.com/desktop/install/linux/
2. **Git** - https://git-scm.com/

You will also need an **OpenAI API key** from https://platform.openai.com/api-keys.

---

## Quick Start

### 1. Clone the repo and switch to the workshop branch

```bash
git clone <repo-url>
cd study_assistant_ai_workshop
git checkout iit-bhu
```

### 2. Create your `.env` file

```bash
cp .env.template .env
```

Open `.env` in any editor and paste your OpenAI API key:

```
OPENAI_API_KEY=sk-proj-...
```

### 3. Verify setup

```bash
cd setup
python3 setup_check.py   # or: python setup_check.py on Windows
```

### 4. Open in a dev container (recommended)

If you use **VS Code** or **Cursor**:
1. Open the repo folder.
2. You should see a prompt to "Reopen in Container". Accept it.
3. Wait for the container to build and install dependencies.
4. In the container terminal, run:

```bash
npm run start
```

5. Open http://localhost:5173 in your browser.

### 4b. Alternative: plain Docker Compose

```bash
docker compose up -d
docker compose exec app bash
npm run start
```

Then open http://localhost:5173.

---

## What Happens Inside the Container

The dev container image includes:
- Python 3.11
- Node.js 22
- `uv` (Python package manager)
- `npm`

On first open, the `postCreateCommand` in `devcontainer.json` runs:

```
npm install && npm --prefix frontend install && uv sync --directory backend
```

This installs all frontend and backend dependencies automatically.

---

## Troubleshooting

### Docker is not running

Make sure Docker Desktop is started. On Linux, check that the Docker daemon is active:

```bash
sudo systemctl status docker
```

### Port already in use

The app uses ports `5173` (frontend) and `8002` (backend). If another process is using them, stop it or change the ports in `docker-compose.yml`.

### `.env` not found errors

Run `cp .env.template .env` and set your `OPENAI_API_KEY`.

### Container build fails

Try rebuilding from scratch:

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## Local Development (Without Docker)

If you prefer running without containers:

1. Install Python 3.11+, Node.js 22+, and `uv`.
2. Run:

```bash
cp .env.template .env
npm install
npm run start
```

This starts both the backend and frontend concurrently.
