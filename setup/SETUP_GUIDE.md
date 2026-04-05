# Setup Guide

This guide is for workshop participants. The goal is to get everyone to a working app with the fewest machine-specific issues.

## Recommended Path

Use the devcontainer if possible.

Best supported:
- `VS Code` + Dev Containers
- `Cursor` + Dev Containers
- `PyCharm` + Dev Containers

Why the devcontainer is preferred:
- Python, Node.js, and `uv` are preinstalled
- fewer host-machine dependency issues
- same setup on Windows, macOS, and Linux
- easier to support in a live workshop

## What You Need Before The Workshop

Prepare these before the session starts:

1. Install Docker Desktop.
2. Install one editor:
   - `VS Code`, `Cursor`, or `PyCharm`
   - devcontainer setup is recommended when available
3. Install Git.
4. Create an OpenAI API key.
5. Download or clone this repo in advance.

## OS-Specific Prerequisites

### Windows

- Install Docker Desktop.
- During Docker installation, enable the `WSL 2` backend.
- Make sure Docker Desktop is running before opening the project.
- If possible, keep your repo inside your normal user folder or WSL home directory, not a network drive.

Recommended quick checks:

```powershell
wsl --status
docker --version
git --version
```

### macOS

- Install Docker Desktop.
- Launch Docker Desktop once and wait until it says Docker is running.
- Install Git if it is not already available.

Quick checks:

```bash
docker --version
git --version
```

### Linux

- Install Docker Engine or Docker Desktop.
- Ensure your user can run Docker without `sudo`.
- Log out and back in if you just added yourself to the `docker` group.

Quick checks:

```bash
docker --version
git --version
```

## Editor Paths

### VS Code Devcontainer Path

1. Install `VS Code`.
2. Install the `Dev Containers` extension.
3. Clone the repo:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent
code .
```

4. When prompted, click `Reopen in Container`.
5. Wait for the first container build to finish.
6. In the integrated terminal:

```bash
cp .env.template .env
```

7. Edit `.env` and set:

```env
OPENAI_API_KEY=your-key-here
```

8. Start the app:

```bash
npm run start
```

9. Open `http://localhost:5173`.

If you want to do the exercises during the workshop:

```bash
./workshop/create_scaffold_branch.sh
git switch workshop-scaffold
./workshop/workshop.sh status
```

### Cursor Devcontainer Path

Cursor follows the same recommended path as VS Code.

1. Install `Cursor`.
2. Install the `Dev Containers` extension if it is not already available.
3. Clone the repo:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent
cursor .
```

4. Use `Reopen in Container`.
5. Wait for the first build.
6. In the terminal:

```bash
cp .env.template .env
```

7. Add your OpenAI key to `.env`.
8. Start the app:

```bash
npm run start
```

9. Open `http://localhost:5173`.

Optional workshop branch:

```bash
./workshop/create_scaffold_branch.sh
git switch workshop-scaffold
```

### PyCharm Devcontainer Path

PyCharm also supports devcontainers, so you can use the same containerized workshop setup there.

1. Install `PyCharm`.
2. Make sure Docker Desktop is installed and running.
3. Clone the repo:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent
```

4. Open the project in `PyCharm`.
5. Use the IDE's devcontainer workflow to open the project in the container.
6. In the terminal inside the container:

```bash
cp .env.template .env
```

7. Add your OpenAI key to `.env`.
8. Start the app:

```bash
npm run start
```

9. Open `http://localhost:5173`.

Optional workshop branch:

```bash
./workshop/create_scaffold_branch.sh
git switch workshop-scaffold
```

## First Run Checklist

Once the app is running:

1. Open `http://localhost:5173`.
2. Upload `resources/documents/CPU.md`.
3. Ask: `What is an instruction pointer?`
4. Ask: `Create revision notes about CPU architecture and save them`.
5. Confirm a file appears in `workshop_notes/`.

If all of that works, your setup is ready.

## Workshop Exercise Flow

The workshop branch starts fully working. During the session, you strip exactly one checkpoint at a time.

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

## Generic Local Setup (Without Devcontainer)

Use this only if you do not want to use a devcontainer. These steps work regardless of editor.

Prerequisites:
- Python `3.11+`
- Node.js `22`
- `uv`
- Git
- OpenAI API key

Setup:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent

cp .env.template .env
# Edit .env and set OPENAI_API_KEY

uv sync
npm install
npm run start
```

Open `http://localhost:5173`.

Optional workshop branch:

```bash
./workshop/create_scaffold_branch.sh
git switch workshop-scaffold
./workshop/workshop.sh status
```

If you use `nvm`:

```bash
nvm install 22
nvm use 22
```

## Troubleshooting

### Docker or Devcontainer Problems

Problem: Container does not start.

Check:
- Docker Desktop is running
- on Windows, WSL 2 is enabled
- you have enough free disk space

Problem: `Reopen in Container` is missing.

Check:
- the `Dev Containers` extension is installed
- you opened the repo root, not a subfolder

### App Start Problems

Problem: `npm run start` fails with Node errors.

Check:

```bash
node -v
```

You should be on Node `22`. In the devcontainer this is automatic.

Problem: Python dependency issues on local setup.

Try:

```bash
uv sync
```

Problem: frontend loads but chat is blank.

Check your internet connection. The ChatKit web component loads from `cdn.platform.openai.com`.

Problem: app starts but answers say no study material was found.

Upload a document first, for example `resources/documents/CPU.md`.

Problem: notes fail to save on first try.

Retry once. The filesystem MCP server can be slow on cold start.

Problem: port `5173` or `8002` is already in use.

Stop the existing process or restart Docker/editor terminals.

## References

Student-facing:
- `README.md`
- `setup/SETUP_GUIDE.md`

Instructor/reference:
- `resources/DEMO_PLAYBOOK.md`
- `resources/AGENTS_PRESENTATION.md`
- `resources/code_examples/`
