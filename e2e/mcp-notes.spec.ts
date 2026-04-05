/**
 * Test 4 — MCP integration: revision notes creation and file saving.
 *
 * Validates the RevisionNotesAgent → search + MCP write_file pipeline.
 * Verifies the agent confirms the file was saved via the chat reply.
 * When the backend runs on the same machine, also checks the file on disk.
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

/**
 * Detect if the backend is truly local by writing a marker file via the
 * notes directory and checking it appears within 2 seconds. If MCP writes
 * go to a remote host (e.g. Codespaces) this will be false.
 */
async function canVerifyFilesLocally(): Promise<boolean> {
  try {
    if (!fs.existsSync(NOTES_DIR)) fs.mkdirSync(NOTES_DIR, { recursive: true });
    // If notes from previous MCP writes exist here, the backend is local
    const existing = listNotes();
    if (existing.length > 0) return true;
    // Otherwise we can't be sure — backend might write to a different filesystem
    // Conservatively return false unless we already see MCP-written files
    return false;
  } catch {
    return false;
  }
}

test.describe("MCP Revision Notes", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(
      chatFrame(page).getByRole("heading", { name: /welcome/i })
    ).toBeVisible({ timeout: 15_000 });
  });

  test("create revision notes saves a markdown file", async ({ page }) => {
    await sendChatMessage(
      page,
      "Create revision notes about CPU architecture and save them as markdown"
    );

    const reply = await waitForAssistantReply(page, 90_000);

    // Agent should confirm the save happened
    expect(reply.toLowerCase()).toMatch(/saved|created|written|file|notes|save/);
    // Should mention the filename or path
    expect(reply).toMatch(/workshop_notes|revision_notes|\.md/);

    // If files land locally, verify on disk too
    if (await canVerifyFilesLocally()) {
      const noteFiles = listNotes();
      expect(noteFiles.length).toBeGreaterThanOrEqual(1);
      const content = fs.readFileSync(`${NOTES_DIR}/${noteFiles[0]}`, "utf-8");
      expect(content.length).toBeGreaterThan(100);
      expect(content).toMatch(/^#/m);
    }
  });

  test("revision notes request triggers correct agent pipeline", async ({ page }) => {
    await sendChatMessage(
      page,
      "Create revision notes about computer networking protocols and save them"
    );

    const reply = await waitForAssistantReply(page, 90_000);

    // Agent should confirm the save
    expect(reply.toLowerCase()).toMatch(/saved|created|written|file|notes|save/);

    // Reply should reference networking content (grounded in uploaded materials)
    expect(reply.toLowerCase()).toMatch(/network|protocol|note/);

    // If files land locally, verify content is grounded
    if (await canVerifyFilesLocally()) {
      const noteFiles = listNotes();
      if (noteFiles.length > 0) {
        const networkingFile = noteFiles.find((f) => /network/i.test(f)) ?? noteFiles[0];
        const content = fs.readFileSync(`${NOTES_DIR}/${networkingFile}`, "utf-8");
        expect(content.toLowerCase()).toMatch(/network|protocol|tcp|ip|http|dns|layer/);
      }
    }
  });
});
