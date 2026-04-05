/**
 * Test 0 — Pre-flight: health check + seed documents.
 *
 * This runs first and ensures the backend and frontend are reachable,
 * then uploads the sample documents that later tests depend on.
 */
import { test, expect } from "@playwright/test";
import {
  API_URL,
  deleteAllDocsViaAPI,
  uploadDocViaAPI,
  listDocsViaAPI,
  SAMPLE_DOCS,
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

  test("clean slate — delete all existing documents and notes", async () => {
    await deleteAllDocsViaAPI();
    clearNotes();
    const docs = await listDocsViaAPI();
    expect(docs).toHaveLength(0);
  });

  test("upload all sample documents", async () => {
    for (const doc of SAMPLE_DOCS) {
      await uploadDocViaAPI(doc);
    }
    const docs = await listDocsViaAPI();
    expect(docs.length).toBe(SAMPLE_DOCS.length);

    const names = docs.map((d) => d.filename);
    for (const expected of SAMPLE_DOCS) {
      expect(names).toContain(expected);
    }
  });
});
