const BASE = "/exam-assistant";

export interface DocumentInfo {
  id: string;
  filename: string;
  summary: string;
  description: string;
  num_chunks: number;
  uploaded_at: string;
  size_bytes: number;
}

export async function fetchDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${BASE}/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  const data = await res.json();
  return data.documents;
}

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  // >>> EXERCISE_10_START
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/documents/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
  // >>> EXERCISE_10_END
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
}

export function getDocumentFileUrl(id: string): string {
  return `${BASE}/documents/${id}/file`;
}
