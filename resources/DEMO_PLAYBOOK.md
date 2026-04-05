# Workshop Demo Playbook

## What Works

| Feature | Status | Notes |
|---------|--------|-------|
| Document upload (PDF, MD, TXT, HTML, DOCX, JSON) | ✅ | AI generates summary + description on upload |
| Document list, preview, delete | ✅ | Preview shows raw text for MD/TXT, iframe for PDF |
| Chat with streaming responses | ✅ | Full SSE streaming via ChatKit |
| Triage → CourseMaterialAgent handoff | ✅ | Routes content questions automatically |
| Triage → RevisionNotesAgent handoff | ✅ | Routes "create/save notes" requests |
| Tool calling (search, list, topic summary) | ✅ | Agent autonomously calls tools |
| RAG retrieval with citations | ✅ | Keyword TF search over chunks, cites [Source: file \| section] |
| MCP filesystem (save revision notes) | ⚠️ | Works but may fail on first cold-start attempt (retry works) |
| Dark/light theme toggle | ✅ | Syncs with ChatKit colorScheme |
| Demo logging in terminal | ✅ | Shows 🤖🔀🔧✅ emoji trail of agent lifecycle |
| Devcontainer | ✅ | Python 3.11 + Node 22 + uv pre-installed |

## Known Issues

1. **MCP cold-start error**: The first "save revision notes" request after server start may fail with a stream error. The MCP filesystem server needs a moment to connect. **Workaround**: Retry the message, or send a simple question first to warm up the MCP connection.

2. **Logfire `instrument_fastapi` warning**: Shows `missing 1 required positional argument: 'app'` on startup. Harmless — logfire API changed. Does not affect functionality.

3. **ChatKit requires internet**: The `<openai-chatkit>` web component loads from `cdn.platform.openai.com`. No internet = no chat panel.

4. **In-memory thread store**: Chat history is lost on server restart. This is by design for the workshop demo.

---

## Demo-Ready Playbook (for instructor)

### Pre-Workshop Setup (do this before students arrive)

```bash
# 1. Ensure .env has your API key
./workshop/init_env.sh
# Edit .env and verify OPENAI_API_KEY is set

# 2. Run a quick host preflight if needed
./workshop/preflight.sh

# 3. Start the app
nvm use 22
npm run start

# 4. Confirm backend/frontend are reachable
./workshop/healthcheck.sh

# 5. Upload sample documents (so there's data to demo with)
curl -X POST http://localhost:8002/exam-assistant/documents/upload \
  -F "file=@resources/documents/CPU.md"
curl -X POST http://localhost:8002/exam-assistant/documents/upload \
  -F "file=@resources/documents/Numpy.md"

# 6. Warm up MCP (send one message to trigger connection)
# Just open http://localhost:5173 and ask "Hi"

# 7. Verify terminal shows emoji logging
# You should see: 🤖 Agent started: TriageAgent
```

### Live Demo Script (10 minutes)

Open two windows side by side:
- **Left**: Browser at `http://localhost:5173`
- **Right**: Terminal running `npm run start` (showing the backend logs)

#### Demo 1: Upload + Simple Q&A (3 min)

1. In browser, upload `resources/documents/CPU.md`
2. Point out: AI generated description + summary automatically
3. Ask: **"What is an instruction pointer?"**
4. Show terminal:
   ```
   🤖 Agent started: TriageAgent
   🔀 Handoff:       TriageAgent → CourseMaterialAgent
   🤖 Agent started: CourseMaterialAgent
   🔧 Tool call:     CourseMaterialAgent → search_uploaded_materials
      Tool result:   search_uploaded_materials → [Source: CPU.md | chunk-1]...
   ✅ Agent done:    CourseMaterialAgent → ...
   ```
5. Explain: "The triage agent decided this is a content question, handed off to the specialist, which called our search tool to find relevant chunks from CPU.md"

#### Demo 2: Multi-Agent Routing (2 min)

1. Ask: **"Hello, how are you?"**
2. Show terminal: only `TriageAgent` runs (no handoff — handles greetings directly)
3. Ask: **"Create revision notes about CPU and save them"**
4. Show terminal:
   ```
   🔀 Handoff:       TriageAgent → RevisionNotesAgent
   🔧 Tool call:     RevisionNotesAgent → search_uploaded_materials
   🔧 Tool call:     RevisionNotesAgent → write_file (MCP)
   ```
5. Open `workshop_notes/` folder — show the saved markdown file

#### Demo 3: Structured Output (2 min)

1. Ask: **"Give me a topic summary about system calls"**
2. Show terminal: `generate_topic_summary` tool call with structured result
3. Explain: "The tool returns a Pydantic model (TopicSummary) — topic, key_concepts, summary, difficulty_level — not free-form text"

#### Demo 4: Theme + Preview (1 min)

1. Toggle dark mode
2. Click preview on a document — show the modal
3. Delete a document — show confirmation dialog

### Demo Messages Cheat Sheet

| Message | What it triggers | Terminal shows |
|---------|-----------------|---------------|
| "Hi there!" | Triage responds directly | 🤖 TriageAgent only |
| "What does my CPU doc say about registers?" | Handoff → CourseMaterial → search tool | 🔀🔧 full pipeline |
| "Summarize all my documents" | Handoff → CourseMaterial → list + search tools | 🔀🔧🔧 |
| "Give me a topic summary about CPU" | Handoff → CourseMaterial → search + generate_topic_summary | 🔀🔧🔧 structured output |
| "Create revision notes and save them" | Handoff → RevisionNotes → search + MCP write_file | 🔀🔧🔧 MCP |

---

## Hands-On Checkpoints Guide (for instructor)

### Student Setup Instructions

Tell students to use the devcontainer if possible. VS Code, Cursor, and PyCharm all support that path. If someone does not want to use a devcontainer, the generic local setup path is also fine.

Point students to `README.md` as the only student-facing setup guide.

Student setup commands:

```bash
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b bhu
cd Exam-Preparation-AI-Agent

# Optional but recommended before opening the IDE:
./workshop/preflight.sh

# Open in devcontainer if using VS Code, Cursor, or PyCharm.
# Then in the terminal:
./workshop/init_env.sh
# Edit .env and add OPENAI_API_KEY

# Start the full working app
npm run start

# Confirm the app is reachable
./workshop/healthcheck.sh
```

If you want students to use the checkpoint workflow, tell them to create a local workshop branch after the app is running:

```bash
./workshop/create_scaffold_branch.sh
git switch workshop-scaffold
./workshop/workshop.sh status
```

Important:
- the branch starts fully working
- students can run the app end-to-end before any exercise is stripped
- only one checkpoint can be active at a time
- students must run `solve N` before moving to the next checkpoint

### Running Checkpoints In Class

Before each checkpoint, say:

> "Keep `npm run start` running. Your app should still work except for the one concept we are about to strip. Now run `./workshop/workshop.sh checkpoint N`."

After students strip a checkpoint:
- tell them to read the `# TODO:` comments
- tell them to use the file list printed by the script
- let them test immediately in the running app

If students get stuck, say:

> "Run `./workshop/workshop.sh solve N` to restore the golden implementation. Then verify the app works again before moving on."

### Checkpoint 1: Implement a Tool (~10-15 min)

**Teach first**:
- Slides 2-8
- Show `resources/code_examples/1_basic_chat.py`
- Show `resources/code_examples/2_multiturn_conversation.py`
- Show `resources/code_examples/3_tools.py`

**Then checkpoint**:

```bash
./workshop/workshop.sh checkpoint 1
```

**Files students edit**:
- `backend/app/agents_sdk/tools.py`

**What students implement**:
- the `search_uploaded_materials` tool body

**How students test**:
1. Upload `resources/documents/CPU.md`
2. Ask a content question
3. Confirm the answer includes citations

### Checkpoint 2: Define Agent + Wire Handoffs (~10-15 min)

**Teach first**:
- Slides 11-16
- Show `resources/code_examples/5_realworld_agent.py`
- Show `resources/code_examples/7_complete_study_system.py`
- Briefly map those examples to `backend/app/agents_sdk/agents.py`

**Then checkpoint**:

```bash
./workshop/workshop.sh solve 1
./workshop/workshop.sh checkpoint 2
```

**Files students edit**:
- `backend/app/agents_sdk/agents.py`

**What students implement**:
- `course_material_agent = Agent(...)`
- `handoffs=[course_material_agent, revision_notes_agent]`

**How students test**:
1. Ask a normal greeting and show no handoff
2. Ask a course-content question and show the handoff to `CourseMaterialAgent`

### Checkpoint 3: Structured Output + Prompt Engineering (~15-20 min)

**Teach first**:
- Slides 9 and 22
- Show `resources/code_examples/4_structured_output.py`
- Compare `TRIAGE_AGENT_PROMPT` and `REVISION_NOTES_AGENT_PROMPT`
- Explain why prompt structure matters before students write their own prompt

**Then checkpoint**:

```bash
./workshop/workshop.sh solve 2
./workshop/workshop.sh checkpoint 3
```

**Files students edit**:
- `backend/app/agents_sdk/tools.py`
- `backend/app/agents_sdk/prompts.py`

**What students implement**:
- `TopicSummary` fields
- `generate_topic_summary` fallback return
- `COURSE_MATERIAL_AGENT_PROMPT`

**How students test**:
1. Ask for a topic summary
2. Check that the answer is structured and grounded
3. Check that the agent behavior improves after the prompt is restored

### Checkpoint 4: MCP Integration (~10-15 min)

**Teach first**:
- Slides 23-25
- Show `resources/code_examples/8_mcp.py`
- Explain that this checkpoint gives the notes agent write access to `workshop_notes/`

**Then checkpoint**:

```bash
./workshop/workshop.sh solve 3
./workshop/workshop.sh checkpoint 4
```

**Files students edit**:
- `backend/app/agents_sdk/mcp.py`

**What students implement**:
- filesystem `MCPServerStdio` config
- MCP connection logic

**How students test**:
1. Ask the app to create revision notes
2. Confirm a file appears in `workshop_notes/`
3. If the first attempt fails, retry once because MCP can be slow on cold start

---

## Suggested Workshop Runbook (2.5-3 Hours)

This sequencing works well because students always start with a fully working app, and each checkpoint removes only one concept at a time.

### Recommended Flow

1. Let students get the app running first.
2. Show the working system end-to-end before teaching internals.
3. Teach one concept cluster.
4. Strip exactly one checkpoint.
5. Let students implement and test in the real app.
6. Restore with `solve N` before moving to the next checkpoint.

### 2.5-Hour Version

| Time | Duration | Activity |
|------|----------|----------|
| 0:00 | 15 min | Setup verification: Docker running, editor open, `.env` configured, app started |
| 0:15 | 10 min | Live product demo: upload doc, ask question, save revision notes |
| 0:25 | 20 min | Slides 1-8: LLMs, chat, agents, tools |
| 0:45 | 15 min | Show code examples `1_basic_chat.py`, `2_multiturn_conversation.py`, `3_tools.py` |
| 1:00 | 15 min | Checkpoint 1 |
| 1:15 | 20 min | Slides 11-16: Agents SDK, multi-agent systems, handoffs |
| 1:35 | 10 min | Show code examples `5_realworld_agent.py` and `7_complete_study_system.py` |
| 1:45 | 15 min | Checkpoint 2 |
| 2:00 | 10 min | Break |
| 2:10 | 10 min | Slides 9 and 22: structured outputs and prompting |
| 2:20 | 15 min | Checkpoint 3 |
| 2:35 | 10 min | Slides 23-25: MCP |
| 2:45 | 10 min | Checkpoint 4 |
| 2:55 | 5 min | Wrap-up and Q&A |

### 3-Hour Version

Use this if you want a slower pace and more student coding time.

| Time | Duration | Activity |
|------|----------|----------|
| 0:00 | 20 min | Setup verification and app bring-up |
| 0:20 | 10 min | Live demo of the finished app |
| 0:30 | 25 min | Slides 1-8 + short discussion |
| 0:55 | 15 min | Code examples `1_basic_chat.py`, `2_multiturn_conversation.py`, `3_tools.py` |
| 1:10 | 15 min | Checkpoint 1 |
| 1:25 | 20 min | Slides 11-16 |
| 1:45 | 10 min | Code examples `5_realworld_agent.py`, `7_complete_study_system.py` |
| 1:55 | 15 min | Checkpoint 2 |
| 2:10 | 10 min | Break |
| 2:20 | 15 min | Slides 9 and 22 + prompt-writing discussion |
| 2:35 | 20 min | Checkpoint 3 |
| 2:55 | 10 min | Slides 23-25 + `8_mcp.py` |
| 3:05 | 15 min | Checkpoint 4 |
| 3:20 | 10 min | Final demo, recap, and Q&A |

### Teaching Tips

- Keep `npm run start` visible in one terminal during demos so students can see handoffs and tool calls.
- Ask students to upload `resources/documents/CPU.md` first so everyone tests against the same document.
- After each checkpoint, tell students to verify the app from the browser, not just from reading code.
- Avoid moving to the next checkpoint until most students have either solved the current one or restored it with `solve N`.
- If setup is taking too long, have students pair up so the workshop stays on schedule.
