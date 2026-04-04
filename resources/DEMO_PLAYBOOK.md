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
cat .env  # verify OPENAI_API_KEY is set

# 2. Start the app
nvm use 22
npm run start

# 3. Upload sample documents (so there's data to demo with)
curl -X POST http://localhost:8002/exam-assistant/documents/upload \
  -F "file=@resources/documents/CPU.md"
curl -X POST http://localhost:8002/exam-assistant/documents/upload \
  -F "file=@resources/documents/Numpy.md"

# 4. Warm up MCP (send one message to trigger connection)
# Just open http://localhost:5173 and ask "Hi"

# 5. Verify terminal shows emoji logging
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

### Setup (tell students)

```bash
# Students clone the scaffold branch
git clone https://github.com/regalmoix/Exam-Preparation-AI-Agent.git -b scaffold
cd Exam-Preparation-AI-Agent

# Open in devcontainer (or set up locally)
# Configure .env with API key
cp .env.template .env
# Edit .env → add OPENAI_API_KEY

# Start the app (everything works — it's the golden solution)
npm run start

# Check checkpoint status
./workshop/workshop.sh status
```

### Running Checkpoints

Before each checkpoint, the instructor says:

> "Now let's implement this ourselves. Run `./workshop/workshop.sh checkpoint N` to strip the code for this exercise."

After ~10 minutes, if students are stuck:

> "If you need help, run `./workshop/workshop.sh solve N` to see the solution and move on."

### Checkpoint 1: Implement a Tool (~10 min)

**Slide context**: After Slides 7-8 (Tools / Function Calling)

```bash
./workshop/workshop.sh checkpoint 1
```

**What's stripped**: `search_uploaded_materials` function body in `tools.py`

**What students write**:
```python
results: list[SearchResult] = retrieval.search(query, top_k=5)
if not results:
    return "No relevant content found in the uploaded materials."
parts: list[str] = []
for r in results:
    parts.append(f"[Source: {r.filename} | {r.section_label}]\n{r.text}\n")
return "\n---\n".join(parts)
```

**Test**: Upload a document, ask about its content → should get cited answer.

### Checkpoint 2: Define Agent + Wire Handoffs (~10 min)

**Slide context**: After Slides 14-16 (Multi-Agent Systems)

```bash
./workshop/workshop.sh checkpoint 2
```

**What's stripped**: `course_material_agent = Agent(...)` and `handoffs=[...]` in `agents.py`

**What students write**:
```python
# Exercise 5
course_material_agent = Agent(
    name="CourseMaterialAgent",
    instructions=COURSE_MATERIAL_AGENT_PROMPT,
    model=OPENAI_DEFAULT_MODEL,
    tools=[search_uploaded_materials, list_uploaded_materials, generate_topic_summary],
)

# Exercise 6 (inside triage_agent)
handoffs=[course_material_agent, revision_notes_agent],
```

**Test**: Ask a content question → should see handoff in terminal.

### Checkpoint 3: Structured Output + Prompt Engineering (~10 min)

**Slide context**: After Slides 9 + 22 (Structured Outputs + Prompting Best Practices)

```bash
./workshop/workshop.sh checkpoint 3
```

**What's stripped**: `TopicSummary` fields, `generate_topic_summary` return, and `COURSE_MATERIAL_AGENT_PROMPT`

**What students write**: Pydantic fields, tool return, and a structured prompt with ## Workflow and ## Rules sections. They have `TRIAGE_AGENT_PROMPT` and `REVISION_NOTES_AGENT_PROMPT` as reference.

**Test**: Ask for a topic summary → should get structured response.

### Checkpoint 4: MCP Integration (~10 min)

**Slide context**: After Slides 23-25 (MCP)

```bash
./workshop/workshop.sh checkpoint 4
```

**What's stripped**: `MCPServerStdio` config and `connect_mcp` body in `mcp.py`

**What students write**:
```python
# 7a
filesystem_mcp_server = MCPServerStdio(
    name="filesystem",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem",
                 str(APP_NOTES_DIR.resolve())],
    },
)

# 7b
try:
    if filesystem_mcp_server.session is None:
        await filesystem_mcp_server.connect()
        revision_notes_agent.mcp_servers = [filesystem_mcp_server]
        available_tools = await filesystem_mcp_server.list_tools()
        logger.info(f"MCP connected. Tools: {[t.name for t in available_tools]}")
except Exception as e:
    logger.error(f"Failed to connect MCP: {e}")
    await filesystem_mcp_server.cleanup()
```

**Test**: Ask to create revision notes → check `workshop_notes/` folder.

---

## Suggested 2.5-Hour Timeline

| Time | Duration | Activity |
|------|----------|----------|
| 0:00 | 30 min | Slides 1-7: LLM → Chat API → Agents → Tools |
| 0:30 | 10 min | **Checkpoint 1**: Implement search tool |
| 0:40 | 25 min | Slides 8-16: Code examples → Multi-agent → Handoffs |
| 1:05 | 10 min | **Checkpoint 2**: Agent + Handoffs |
| 1:15 | 15 min | Slides 9, 22: Structured Outputs + Prompting Best Practices |
| 1:30 | 10 min | **Checkpoint 3**: Structured output + Prompt |
| 1:40 | 10 min | Break |
| 1:50 | 15 min | Slides 20-25: RAG + MCP |
| 2:05 | 10 min | **Checkpoint 4**: MCP integration |
| 2:15 | 15 min | Q&A + Wrap-up |
