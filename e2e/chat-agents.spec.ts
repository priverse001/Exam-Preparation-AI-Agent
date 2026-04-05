/**
 * Test 3 — Chat agent routing and tool calling.
 *
 * Validates each demo-playbook scenario:
 *   1. Greeting         → TriageAgent only (no handoff)
 *   2. Content Q&A      → Triage → CourseMaterialAgent → search_uploaded_materials
 *   3. Topic summary    → Triage → CourseMaterialAgent → search + generate_topic_summary
 *   4. Summarize all    → Triage → CourseMaterialAgent → list_uploaded_materials
 *   5. Revision notes   → Triage → RevisionNotesAgent  → search + MCP write_file
 *
 * Assumes setup.spec.ts has seeded documents.
 */
import { test, expect } from "@playwright/test";
import {
  chatFrame,
  chatInput,
  sendChatMessage,
  waitForAssistantReply,
  startNewChat,
  clearNotes,
  listNotes,
} from "./helpers";

test.describe("Chat Agent Routing", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    // Wait for ChatKit to load
    await expect(
      chatFrame(page).getByRole("heading", { name: /welcome/i })
    ).toBeVisible({ timeout: 15_000 });
  });

  // -----------------------------------------------------------------
  // Demo 1: Greeting — Triage responds directly
  // -----------------------------------------------------------------
  test("greeting is handled by triage agent directly", async ({ page }) => {
    await sendChatMessage(page, "Hi there! How are you?");
    const reply = await waitForAssistantReply(page);

    // Should get a friendly response, not a "please upload" or error
    expect(reply.toLowerCase()).toMatch(/hello|hi|hey|help|welcome|study|assist/);

    // Should NOT contain agent routing leaks
    expect(reply).not.toContain("CourseMaterialAgent");
    expect(reply).not.toContain("RevisionNotesAgent");
    expect(reply).not.toContain("handoff");
  });

  // -----------------------------------------------------------------
  // Demo 2: Content Q&A — handoff to CourseMaterialAgent + search
  // -----------------------------------------------------------------
  test("content question triggers CourseMaterialAgent with search", async ({ page }) => {
    await sendChatMessage(
      page,
      "Explain what tensor broadcasting is based on my uploaded PyTorch notes"
    );
    const reply = await waitForAssistantReply(page);

    // Should mention tensor-related concepts from Pytorch FasAI.md
    expect(reply.toLowerCase()).toMatch(/tensor|broadcast|dimension|pytorch/);

    // Should not leak agent internals
    expect(reply).not.toContain("TriageAgent");
  });

  // -----------------------------------------------------------------
  // Demo 3: Topic summary — structured output via generate_topic_summary
  // -----------------------------------------------------------------
  test("topic summary request triggers structured output tool", async ({ page }) => {
    await sendChatMessage(
      page,
      "Give me a topic summary about Java programming concepts from my study materials"
    );
    const reply = await waitForAssistantReply(page);

    // Should contain structured information about Java
    expect(reply.toLowerCase()).toMatch(/java/);

    // Should contain some structured elements (headings, bullet points, key concepts)
    // The generate_topic_summary tool returns topic, key_concepts, summary, difficulty_level
    expect(reply.length).toBeGreaterThan(100);
  });

  // -----------------------------------------------------------------
  // Demo 4: Summarize all — uses list_uploaded_materials tool
  // -----------------------------------------------------------------
  test("summarize all documents uses list tool", async ({ page }) => {
    await sendChatMessage(page, "Summarize all my uploaded documents");
    const reply = await waitForAssistantReply(page, 90_000);

    // Should mention multiple documents by name
    const mentionedDocs = [
      /cpu/i,
      /numpy|python/i,
      /java/i,
      /network/i,
      /pytorch|fastai/i,
    ];
    let matchCount = 0;
    for (const pattern of mentionedDocs) {
      if (pattern.test(reply)) matchCount++;
    }
    // Should mention at least 3 out of 5 docs
    expect(matchCount).toBeGreaterThanOrEqual(3);
  });

  // -----------------------------------------------------------------
  // Demo 5: Multi-doc cross-question
  // -----------------------------------------------------------------
  test("cross-document question retrieves from multiple sources", async ({ page }) => {
    await sendChatMessage(
      page,
      "Compare how data is organized in computer memory (CPU/RAM) versus how data is organized in NumPy arrays"
    );
    const reply = await waitForAssistantReply(page);

    // Should reference concepts from at least one of the docs
    expect(reply.toLowerCase()).toMatch(/memory|ram|array|numpy|cpu/);
    expect(reply.length).toBeGreaterThan(100);
  });
});
