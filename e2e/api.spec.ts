/**
 * Test 6 — REST API endpoints: health, documents CRUD, file download.
 */
import { test, expect } from "@playwright/test";
import * as path from "path";
import * as fs from "fs";
import { API_URL, DOCS_DIR } from "./helpers";

test.describe("REST API", () => {
  test("GET /health returns healthy", async () => {
    const res = await fetch(`${API_URL}/health`);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toEqual({ status: "healthy" });
  });

  test("GET /documents returns list with expected fields", async () => {
    const res = await fetch(`${API_URL}/documents`);
    expect(res.status).toBe(200);
    const body = (await res.json()) as {
      documents: {
        id: string;
        filename: string;
        summary: string;
        description: string;
        num_chunks: number;
        size_bytes: number;
        uploaded_at: string;
      }[];
    };
    expect(body.documents.length).toBeGreaterThan(0);

    const doc = body.documents[0];
    expect(doc.id).toBeTruthy();
    expect(doc.filename).toBeTruthy();
    expect(doc.summary.length).toBeGreaterThan(10);
    expect(doc.description.length).toBeGreaterThan(5);
    expect(doc.num_chunks).toBeGreaterThan(0);
    expect(doc.size_bytes).toBeGreaterThan(0);
    expect(doc.uploaded_at).toBeTruthy();
  });

  test("POST /documents/upload + GET /documents/:id + DELETE", async () => {
    // Upload
    const filePath = path.join(DOCS_DIR, "CPU.md");
    const form = new FormData();
    form.append("file", new Blob([fs.readFileSync(filePath)]), "CPU_test.md");
    const uploadRes = await fetch(`${API_URL}/documents/upload`, {
      method: "POST",
      body: form,
    });
    expect(uploadRes.status).toBe(200);
    const uploaded = (await uploadRes.json()) as { id: string; filename: string };
    expect(uploaded.filename).toBe("CPU_test.md");

    // Get single doc metadata
    const getRes = await fetch(`${API_URL}/documents/${uploaded.id}`);
    expect(getRes.status).toBe(200);

    // Download file
    const fileRes = await fetch(`${API_URL}/documents/${uploaded.id}/file`);
    expect(fileRes.status).toBe(200);
    const content = await fileRes.text();
    expect(content).toContain("CPU");

    // Delete
    const delRes = await fetch(`${API_URL}/documents/${uploaded.id}`, {
      method: "DELETE",
    });
    expect(delRes.status).toBe(200);

    // Verify deleted
    const verifyRes = await fetch(`${API_URL}/documents/${uploaded.id}`);
    expect(verifyRes.status).toBe(404);
  });
});
