/**
 * Test 0 — Pre-flight: health check + clean slate + seed documents.
 *
 * This runs first (via Playwright project dependencies) and ensures the
 * backend and frontend are reachable, deletes any leftover documents
 * through the browser UI, then uploads the sample documents that later
 * tests depend on — also through the browser file chooser.
 */
import { test, expect } from "@playwright/test";
import * as path from "path";
import {
  API_URL,
  DOCS_DIR,
  SAMPLE_DOCS,
  listDocsViaAPI,
  clearNotes,
} from "./helpers";

test.describe("Setup & Health Check", () => {
  test("backend health endpoint returns healthy", async () => {
    const res = await fetch(`${API_URL}/health`);
    expect(res.ok).toBe(true);
    const body = await res.json();
    expect(body.status).toBe("healthy");
  });

  test("frontend loads successfully", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Study Assistant/i);
    await expect(page.getByRole("heading", { name: "Study Assistant" })).toBeVisible();
  });

  test("clean slate — delete all documents via UI and clear notes", async ({ page }) => {
    clearNotes();
    await page.goto("/");

    // Accept every confirmation dialog automatically
    page.on("dialog", (dialog) => dialog.accept());

    // Keep clicking delete buttons until none remain
    while (true) {
      const deleteBtn = page.getByRole("button", { name: "Delete" }).first();
      if (!(await deleteBtn.isVisible({ timeout: 2000 }).catch(() => false))) break;
      await deleteBtn.click();
      // Wait for the list to update after deletion
      await page.waitForTimeout(1000);
    }

    // Verify empty state in UI
    await expect(page.getByText("No documents uploaded yet.")).toBeVisible({ timeout: 5000 });

    // Double-check via API
    const docs = await listDocsViaAPI();
    expect(docs).toHaveLength(0);
  });

  test("upload all sample documents via browser file chooser", async ({ page }) => {
    await page.goto("/");

    for (const doc of SAMPLE_DOCS) {
      const [fileChooser] = await Promise.all([
        page.waitForEvent("filechooser"),
        page.locator('label:has-text("Upload Study Materials")').click(),
      ]);
      await fileChooser.setFiles(path.join(DOCS_DIR, doc));

      // Wait for upload + AI summarization to complete (doc appears in sidebar)
      await expect(page.getByText(doc).first()).toBeVisible({ timeout: 30_000 });
    }

    // Verify all docs are listed
    const docs = await listDocsViaAPI();
    expect(docs.length).toBe(SAMPLE_DOCS.length);

    const names = docs.map((d) => d.filename);
    for (const expected of SAMPLE_DOCS) {
      expect(names).toContain(expected);
    }
  });
});
