import { Page, FrameLocator, expect } from "@playwright/test";
import * as path from "path";
import * as fs from "fs";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
export const BASE_URL = "http://localhost:5173";
export const API_URL = "http://localhost:8002/exam-assistant";
export const DOCS_DIR = path.resolve(__dirname, "..", "resources", "documents");
export const NOTES_DIR = path.resolve(__dirname, "..", "workshop_notes");

export const SAMPLE_DOCS = [
  "CPU.md",
  "Numpy.md",
  "Java Notes.md",
  "Computer Networking.md",
  "Pytorch FasAI.md",
];

// ---------------------------------------------------------------------------
// API helpers – faster than UI uploads
// ---------------------------------------------------------------------------

/** Upload a document via the REST API. */
export async function uploadDocViaAPI(filename: string): Promise<void> {
  const filePath = path.join(DOCS_DIR, filename);
  const form = new FormData();
  form.append("file", new Blob([fs.readFileSync(filePath)]), filename);
  const res = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`Upload failed for ${filename}: ${res.status}`);
}

/** Delete all documents via the REST API. */
export async function deleteAllDocsViaAPI(): Promise<void> {
  const res = await fetch(`${API_URL}/documents`);
  if (!res.ok) return;
  const { documents } = (await res.json()) as { documents: { id: string }[] };
  for (const doc of documents) {
    await fetch(`${API_URL}/documents/${doc.id}`, { method: "DELETE" });
  }
}

/** List documents via the REST API. */
export async function listDocsViaAPI(): Promise<{ id: string; filename: string }[]> {
  const res = await fetch(`${API_URL}/documents`);
  if (!res.ok) return [];
  const { documents } = (await res.json()) as { documents: { id: string; filename: string }[] };
  return documents;
}

// ---------------------------------------------------------------------------
// ChatKit iframe helpers
// ---------------------------------------------------------------------------

/** Get the ChatKit iframe locator. */
export function chatFrame(page: Page): FrameLocator {
  return page.frameLocator('iframe[name="chatkit"]');
}

/** Get the chat input textbox. */
export function chatInput(page: Page) {
  return chatFrame(page).getByRole("textbox", { name: /ask about your study/i });
}

/** Send a chat message and wait for a response to appear. */
export async function sendChatMessage(page: Page, message: string): Promise<void> {
  const input = chatInput(page);
  await input.fill(message);
  await input.press("Enter");
  // Wait for the assistant response to start streaming
  await expect(
    chatFrame(page).locator("article").last().getByRole("heading", { name: /assistant said/i })
  ).toBeVisible({ timeout: 30_000 });
}

/**
 * Wait for the assistant's latest reply to stabilize (streaming done).
 * We detect this by waiting until the text stops changing for 3s.
 */
export async function waitForAssistantReply(page: Page, timeoutMs = 60_000): Promise<string> {
  const frame = chatFrame(page);
  const startTime = Date.now();
  let lastText = "";
  let stableCount = 0;

  while (Date.now() - startTime < timeoutMs) {
    const articles = frame.locator("article");
    const count = await articles.count();
    if (count === 0) {
      await page.waitForTimeout(500);
      continue;
    }
    const lastArticle = articles.last();
    const currentText = (await lastArticle.textContent()) ?? "";

    if (currentText === lastText && currentText.length > 30) {
      stableCount++;
      if (stableCount >= 3) return currentText;
    } else {
      stableCount = 0;
    }
    lastText = currentText;
    await page.waitForTimeout(1000);
  }
  return lastText;
}

/** Click the "New chat" button in ChatKit. */
export async function startNewChat(page: Page): Promise<void> {
  const btn = chatFrame(page).getByRole("button", { name: "New chat" });
  if (await btn.isEnabled({ timeout: 3000 }).catch(() => false)) {
    await btn.click();
    await expect(
      chatFrame(page).getByRole("heading", { name: /welcome/i })
    ).toBeVisible({ timeout: 10_000 });
  }
}

// ---------------------------------------------------------------------------
// Notes helpers
// ---------------------------------------------------------------------------

/** Remove all files from the workshop_notes directory. */
export function clearNotes(): void {
  if (!fs.existsSync(NOTES_DIR)) return;
  for (const f of fs.readdirSync(NOTES_DIR)) {
    fs.unlinkSync(path.join(NOTES_DIR, f));
  }
}

/** List files in the workshop_notes directory. */
export function listNotes(): string[] {
  if (!fs.existsSync(NOTES_DIR)) return [];
  return fs.readdirSync(NOTES_DIR).filter((f) => !f.startsWith("."));
}
