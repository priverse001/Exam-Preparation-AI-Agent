/**
 * Test 4 — MCP integration: revision notes creation and file saving.
 *
 * Validates the RevisionNotesAgent → search + MCP write_file pipeline.
 * Checks that a markdown file is actually created on disk.
 */
import { test, expect } from "@playwright/test";
import * as fs from "fs";
import {
  chatFrame,
  sendChatMessage,
  waitForAssistantReply,
  clearNotes,
  listNotes,
  NOTES_DIR,
} from "./helpers";

/** Poll until at least one note file appears on disk (or timeout). */
async function waitForNoteFile(timeoutMs = 60_000): Promise<string[]> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const notes = listNotes();
    if (notes.length > 0) return notes;
    await new Promise((r) => setTimeout(r, 1000));
  }
  return listNotes();
}

test.describe("MCP Revision Notes", () => {
  test.beforeEach(async ({ page }) => {
    clearNotes();
    await page.goto("/");
    await expect(
      chatFrame(page).getByRole("heading", { name: /welcome/i })
    ).toBeVisible({ timeout: 15_000 });
  });

  test("create revision notes saves a markdown file to disk", async ({ page }) => {
    // Verify notes dir is empty
    expect(listNotes()).toHaveLength(0);

    await sendChatMessage(
      page,
      "Create revision notes about CPU architecture and save them as markdown"
    );

    // Wait for the reply to finish streaming
    const reply = await waitForAssistantReply(page, 90_000);

    // Response should mention saving/creating notes
    expect(reply.toLowerCase()).toMatch(/saved|created|written|file|notes|save/);

    // Wait for the file to actually appear on disk (MCP write may lag behind the reply)
    const notes = await waitForNoteFile(30_000);
    expect(notes.length).toBeGreaterThanOrEqual(1);

    // The file should be a non-empty markdown file
    const filePath = `${NOTES_DIR}/${notes[0]}`;
    const content = fs.readFileSync(filePath, "utf-8");
    expect(content.length).toBeGreaterThan(100);
    // Should contain markdown heading
    expect(content).toMatch(/^#/m);
  });

  test("revision notes content is grounded in uploaded materials", async ({ page }) => {
    await sendChatMessage(
      page,
      "Create revision notes about computer networking protocols and save them"
    );

    // Wait for reply and file on disk
    await waitForAssistantReply(page, 90_000);
    const notes = await waitForNoteFile(30_000);
    expect(notes.length).toBeGreaterThanOrEqual(1);

    // Find the networking notes file (or use the first one)
    const networkingFile = notes.find((f) => /network/i.test(f)) ?? notes[0];
    const content = fs.readFileSync(`${NOTES_DIR}/${networkingFile}`, "utf-8");
    // Should reference networking concepts from the uploaded doc
    expect(content.toLowerCase()).toMatch(/network|protocol|tcp|ip|http|dns|layer/);
  });
});
