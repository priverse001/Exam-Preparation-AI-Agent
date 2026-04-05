/**
 * Test 1 — Document Panel: list, preview, delete, upload indicator.
 *
 * Assumes setup.spec.ts has already seeded documents.
 */
import { test, expect } from "@playwright/test";
import {
  SAMPLE_DOCS,
  chatFrame,
  uploadDocViaAPI,
  deleteAllDocsViaAPI,
  listDocsViaAPI,
} from "./helpers";

test.describe("Document Panel", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    // Wait for document list to load
    await expect(page.getByText(/chunks/).first()).toBeVisible({ timeout: 10_000 });
  });

  test("all uploaded documents appear in the sidebar", async ({ page }) => {
    for (const doc of SAMPLE_DOCS) {
      await expect(page.getByText(doc).first()).toBeVisible();
    }
  });

  test("each document shows chunk count and size", async ({ page }) => {
    // At least one doc should show "chunks" and "KB"
    const items = page.locator("li");
    const count = await items.count();
    expect(count).toBeGreaterThanOrEqual(SAMPLE_DOCS.length);

    // Verify chunk + KB pattern
    await expect(page.getByText(/\d+ chunks/).first()).toBeVisible();
    await expect(page.getByText(/KB/).first()).toBeVisible();
  });

  test("preview modal opens and shows summary + content", async ({ page }) => {
    // Click preview on the first document
    const previewBtn = page.getByRole("button", { name: "Preview" }).first();
    await previewBtn.click();

    // Modal should appear with a heading matching a filename
    const modal = page.locator(".fixed.inset-0");
    await expect(modal).toBeVisible();

    // Should show "Summary:" label
    await expect(modal.getByText("Summary:")).toBeVisible();

    // Should show document content (a <pre> tag for text files)
    await expect(modal.locator("pre")).toBeVisible({ timeout: 10_000 });

    // Close modal
    await modal.getByRole("button").first().click();
    await expect(modal).not.toBeVisible();
  });

  test("delete a document with confirmation dialog", async ({ page }) => {
    // Count docs before
    const docsBefore = await listDocsViaAPI();
    const countBefore = docsBefore.length;

    // Accept the confirmation dialog
    page.on("dialog", (dialog) => dialog.accept());

    // Click delete on last document
    const deleteBtn = page.getByRole("button", { name: "Delete" }).last();
    await deleteBtn.click();

    // Wait for the list to update
    await page.waitForTimeout(2000);

    // Count docs after
    const docsAfter = await listDocsViaAPI();
    expect(docsAfter.length).toBe(countBefore - 1);

    // Re-upload the deleted doc so other tests still have all 5
    const deleted = docsBefore.find(
      (d) => !docsAfter.some((a) => a.id === d.id)
    );
    if (deleted) {
      await uploadDocViaAPI(deleted.filename);
    }
  });
});
