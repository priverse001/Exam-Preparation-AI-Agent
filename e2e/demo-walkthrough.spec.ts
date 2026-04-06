/**
 * Full real-life E2E demo walkthrough.
 *
 * This is a single continuous test that simulates a real student session:
 *   1. Start with a completely empty app
 *   2. Upload study documents through the browser
 *   3. Verify they appear in the sidebar
 *   4. Preview a document
 *   5. Start chatting — greeting, Q&A, follow-ups, topic summary
 *   6. Ask to list uploaded documents
 *   7. Ask a cross-document question
 *   8. Request revision notes saved to disk
 *   9. Verify the notes file exists
 *  10. Toggle dark mode and back
 *  11. Delete a document and confirm it's gone
 *
 * Run standalone:
 *   npx playwright test --project=demo --headed
 *
 * In headed mode the config adds slowMo: 600ms so you can watch every action.
 * The test also adds explicit pauses between steps so the viewer can follow along.
 */
import { test, expect } from "@playwright/test";
import * as path from "path";
import * as fs from "fs";

const DOCS_DIR = path.resolve(__dirname, "..", "resources", "documents");
const NOTES_DIR = path.resolve(__dirname, "..", "workshop_notes");
const API_URL = "http://localhost:8002/exam-assistant";

// ── Helpers ──────────────────────────────────────────────────────────────

function chatFrame(page: import("@playwright/test").Page) {
  return page.frameLocator('iframe[name="chatkit"]');
}

function chatInput(page: import("@playwright/test").Page) {
  return chatFrame(page).getByRole("textbox", { name: /ask about your study/i });
}

/** Pause so the viewer can see what just happened (headed mode). */
async function breathe(page: import("@playwright/test").Page, ms = 2000) {
  await page.waitForTimeout(ms);
}

/** Type a message into ChatKit, press Enter, and wait for the reply to finish streaming. */
async function chat(
  page: import("@playwright/test").Page,
  message: string,
  timeoutMs = 90_000,
): Promise<string> {
  // Count existing articles so we know which one is "new"
  const frame = chatFrame(page);
  const articlesBefore = await frame.locator("article").count();

  // Type and send
  const input = chatInput(page);
  await input.fill(message);
  await breathe(page, 800); // let the viewer read what we typed
  await input.press("Enter");

  // Wait for the assistant's response article to appear
  await expect(frame.locator("article").nth(articlesBefore + 1)).toBeVisible({ timeout: 30_000 });

  // Wait for streaming to finish — text stabilises for 3 consecutive 1s checks
  const startTime = Date.now();
  let lastText = "";
  let stable = 0;
  while (Date.now() - startTime < timeoutMs) {
    const text = (await frame.locator("article").last().textContent()) ?? "";
    if (text === lastText && text.length > 80) {
      stable++;
      if (stable >= 3) {
        await breathe(page, 1500); // let viewer read the final answer
        return text;
      }
    } else {
      stable = 0;
    }
    lastText = text;
    await page.waitForTimeout(1000);
  }
  return lastText;
}

// ── The test ─────────────────────────────────────────────────────────────

test.describe("Full Demo Walkthrough", () => {
  // This is a long test — 10+ AI chat round-trips plus uploads and pauses
  test.setTimeout(600_000); // 10 minutes

  test("complete student session — upload, chat, follow-up, notes, cleanup", async ({ page }) => {
    // ================================================================
    //  STEP 0 — Clean slate
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Clean slate — delete all docs and notes" });

    // Clear notes on disk
    if (fs.existsSync(NOTES_DIR)) {
      for (const f of fs.readdirSync(NOTES_DIR)) {
        fs.unlinkSync(path.join(NOTES_DIR, f));
      }
    }

    // Delete all documents via API (faster for setup)
    const existing = await fetch(`${API_URL}/documents`);
    if (existing.ok) {
      const { documents } = (await existing.json()) as { documents: { id: string }[] };
      for (const doc of documents) {
        await fetch(`${API_URL}/documents/${doc.id}`, { method: "DELETE" });
      }
    }

    // ================================================================
    //  STEP 1 — Open the app
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Open app at localhost:5173" });

    await page.goto("/");
    await expect(page).toHaveTitle(/Study Assistant/i);
    await expect(page.getByRole("heading", { name: "Study Assistant" })).toBeVisible();
    await expect(page.getByText("No documents uploaded yet.")).toBeVisible();

    // ChatKit welcome screen
    await expect(chatFrame(page).getByText("Welcome to your AI Study Assistant!")).toBeVisible({
      timeout: 15_000,
    });
    await breathe(page, 2000);

    // ================================================================
    //  STEP 2 — Upload CPU.md through the browser file chooser
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Upload CPU.md via browser file picker" });

    const [chooser1] = await Promise.all([
      page.waitForEvent("filechooser"),
      page.locator('label:has-text("Upload Study Materials")').click(),
    ]);
    await chooser1.setFiles(path.join(DOCS_DIR, "CPU.md"));

    // Wait for it to appear in the sidebar
    await expect(page.getByText("CPU.md").first()).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/chunks/).first()).toBeVisible({ timeout: 10_000 });
    await breathe(page);

    // ================================================================
    //  STEP 3 — Upload Computer Networking.md
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Upload Computer Networking.md" });

    const [chooser2] = await Promise.all([
      page.waitForEvent("filechooser"),
      page.locator('label:has-text("Upload Study Materials")').click(),
    ]);
    await chooser2.setFiles(path.join(DOCS_DIR, "Computer Networking.md"));

    await expect(page.getByText("Computer Networking.md").first()).toBeVisible({ timeout: 30_000 });
    await breathe(page);

    // ================================================================
    //  STEP 4 — Upload Pytorch FasAI.md
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Upload Pytorch FasAI.md" });

    const [chooser3] = await Promise.all([
      page.waitForEvent("filechooser"),
      page.locator('label:has-text("Upload Study Materials")').click(),
    ]);
    await chooser3.setFiles(path.join(DOCS_DIR, "Pytorch FasAI.md"));

    await expect(page.getByText("Pytorch FasAI.md").first()).toBeVisible({ timeout: 30_000 });
    await breathe(page);

    // ================================================================
    //  STEP 5 — Preview CPU.md to see the summary and content
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Preview CPU.md — check summary and raw content" });

    // Find the CPU.md list item and click its preview button
    const cpuItem = page.locator("li", { hasText: "CPU.md" }).first();
    await cpuItem.getByRole("button", { name: "Preview" }).click();

    const modal = page.locator(".fixed.inset-0");
    await expect(modal).toBeVisible();
    await expect(modal.getByText("Summary:")).toBeVisible();
    await expect(modal.locator("pre")).toBeVisible({ timeout: 10_000 });
    await breathe(page, 3000);

    // Close the preview
    await modal.locator("button").first().click();
    await expect(modal).not.toBeVisible();
    await breathe(page, 1000);

    // ================================================================
    //  STEP 6 — Chat: friendly greeting
    //  Expected: TriageAgent responds directly, no handoff
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — say hello (Triage responds directly)" });

    const greetingReply = await chat(page, "Hey! I'm preparing for my CS exam. Can you help me?");
    expect(greetingReply.toLowerCase()).toMatch(/help|welcome|assist|study|happy|course|sure|of course/);
    // Should NOT leak agent internals
    expect(greetingReply).not.toContain("CourseMaterialAgent");
    expect(greetingReply).not.toContain("handoff");

    // ================================================================
    //  STEP 7 — Chat: ask what documents are uploaded
    //  Expected: Triage → CourseMaterialAgent → list_uploaded_materials
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — what docs are uploaded? (list tool)" });

    const listReply = await chat(page, "What documents do I have uploaded?");
    expect(listReply.toLowerCase()).toMatch(/cpu/);
    expect(listReply.toLowerCase()).toMatch(/network/);
    expect(listReply.toLowerCase()).toMatch(/pytorch|fastai/);

    // ================================================================
    //  STEP 8 — Chat: ask a specific content question about CPU
    //  Expected: Triage → CourseMaterialAgent → search_uploaded_materials
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — what is an instruction pointer? (search tool + RAG)" });

    const cpuReply = await chat(page, "What is an instruction pointer? Explain based on my CPU notes.");
    expect(cpuReply.toLowerCase()).toMatch(/instruction pointer|instruction|pointer/);
    expect(cpuReply.toLowerCase()).toMatch(/register|ram|memory|cpu|fetch/);
    // Should be a substantive answer, not a one-liner
    expect(cpuReply.length).toBeGreaterThan(200);

    // ================================================================
    //  STEP 9 — Chat: follow-up question (same thread, tests multi-turn)
    //  Expected: stays in CourseMaterialAgent, searches again
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — follow-up: what about kernel mode? (multi-turn)" });

    const followUpReply = await chat(
      page,
      "Interesting! And what does my document say about kernel mode vs user mode?",
    );
    expect(followUpReply.toLowerCase()).toMatch(/kernel|user mode|privilege|ring/);
    expect(followUpReply.length).toBeGreaterThan(150);

    // ================================================================
    //  STEP 10 — Chat: ask about a different document (networking)
    //  Expected: CourseMaterialAgent searches networking chunks
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — question about networking (cross-doc)" });

    const networkReply = await chat(
      page,
      "Now switching topics — explain the OSI model layers from my networking notes.",
    );
    expect(networkReply.toLowerCase()).toMatch(/layer|osi|network|transport|application|physical/);

    // ================================================================
    //  STEP 11 — Chat: request a topic summary (structured output)
    //  Expected: CourseMaterialAgent → search + generate_topic_summary
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — give me a topic summary about tensors (structured output)" });

    const summaryReply = await chat(
      page,
      "Give me a topic summary about tensor broadcasting from my PyTorch notes.",
    );
    expect(summaryReply.toLowerCase()).toMatch(/tensor|broadcast|dimension/);
    expect(summaryReply.length).toBeGreaterThan(150);

    // ================================================================
    //  STEP 12 — Chat: compare across documents
    //  Expected: CourseMaterialAgent searches multiple docs
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — cross-doc comparison question" });

    const crossDocReply = await chat(
      page,
      "Compare how data flows in a CPU (fetch-execute cycle) versus how data flows in a computer network (packet switching). Use my uploaded notes.",
    );
    expect(crossDocReply.toLowerCase()).toMatch(/cpu|fetch|execute|network|packet|data/);
    expect(crossDocReply.length).toBeGreaterThan(200);

    // ================================================================
    //  STEP 13 — Chat: create revision notes and save (MCP)
    //  Expected: Triage → RevisionNotesAgent → search + write_file
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — create revision notes about CPU and save (MCP write_file)" });

    const notesReply = await chat(
      page,
      "Create comprehensive revision notes about CPU architecture covering instruction pointers, registers, kernel mode, and system calls. Save them as markdown.",
    );
    expect(notesReply.toLowerCase()).toMatch(/saved|created|written|file|notes/);
    // Should reference the file path
    expect(notesReply).toMatch(/workshop_notes|revision_notes|\.md/);

    // If backend is local, also verify the file on disk
    if (fs.existsSync(NOTES_DIR)) {
      const noteFiles = fs.readdirSync(NOTES_DIR).filter((f) => f.endsWith(".md"));
      if (noteFiles.length > 0) {
        const noteContent = fs.readFileSync(path.join(NOTES_DIR, noteFiles[0]), "utf-8");
        expect(noteContent.length).toBeGreaterThan(200);
        expect(noteContent).toMatch(/^#/m); // has markdown headings
        expect(noteContent.toLowerCase()).toMatch(/cpu|instruction|register|kernel/);
      }
    }
    await breathe(page, 2000);

    // ================================================================
    //  STEP 14 — Toggle dark mode
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Toggle dark mode on" });

    await page.getByRole("button", { name: "Toggle theme" }).click();
    await expect(page.locator("html")).toHaveClass(/dark/);
    await breathe(page, 2000);

    // Toggle back to light
    test.info().annotations.push({ type: "step", description: "Toggle back to light mode" });
    await page.getByRole("button", { name: "Toggle theme" }).click();
    await expect(page.locator("html")).not.toHaveClass(/dark/);
    await breathe(page, 1000);

    // ================================================================
    //  STEP 15 — Delete a document via UI
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Delete CPU.md via UI with confirmation" });

    page.on("dialog", (dialog) => dialog.accept());

    const cpuDeleteItem = page.locator("li", { hasText: "CPU.md" }).first();
    await cpuDeleteItem.getByRole("button", { name: "Delete" }).click();
    await breathe(page, 2000);

    // Verify CPU.md is gone from the sidebar
    // (there may be other docs still, so we check CPU.md specifically is missing)
    const remainingDocs = await page.locator("li").allTextContents();
    const cpuStillThere = remainingDocs.some((text) => text.includes("CPU.md"));
    expect(cpuStillThere).toBe(false);

    // ================================================================
    //  STEP 16 — One more chat to confirm the app still works after delete
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Chat — verify app works after delete" });

    const finalReply = await chat(
      page,
      "What documents do I still have uploaded?",
    );
    // Should mention the remaining docs but NOT CPU.md
    expect(finalReply.toLowerCase()).toMatch(/network|pytorch|fastai/);
    expect(finalReply.toLowerCase()).not.toContain("cpu.md");

    await breathe(page, 3000);

    // ================================================================
    //  DONE
    // ================================================================
    test.info().annotations.push({ type: "step", description: "Demo walkthrough complete!" });
  });
});
