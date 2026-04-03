import { useState, useRef, useEffect } from "react";
import { Upload, Trash2, FileText, Eye, X, Loader2 } from "lucide-react";
import { DocumentInfo, uploadDocument, deleteDocument, getDocumentFileUrl } from "../api";

interface Props {
  documents: DocumentInfo[];
  onRefresh: () => Promise<void>;
}

export function DocumentPanel({ documents, onRefresh }: Props) {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState<DocumentInfo | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;

    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        await uploadDocument(file);
      }
      await onRefresh();
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Upload failed. Please try again.");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this document?")) return;
    try {
      await deleteDocument(id);
      await onRefresh();
      if (preview?.id === id) setPreview(null);
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Upload area */}
      <div className="p-3 border-b border-gray-200 dark:border-gray-700">
        <label className="flex items-center justify-center gap-2 px-4 py-2.5 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-gray-800 transition-colors">
          {uploading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Upload size={18} />
          )}
          <span className="text-sm font-medium">
            {uploading ? "Uploading..." : "Upload Study Materials"}
          </span>
          <input
            ref={fileRef}
            type="file"
            multiple
            accept=".pdf,.txt,.md,.html,.docx,.json"
            onChange={handleUpload}
            className="hidden"
            disabled={uploading}
          />
        </label>
        <p className="mt-1.5 text-xs text-gray-500 dark:text-gray-400 text-center">
          PDF, TXT, MD, HTML, DOCX, JSON
        </p>
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto">
        {documents.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500 dark:text-gray-400">
            No documents uploaded yet.
            <br />
            Upload study materials to get started!
          </div>
        ) : (
          <ul className="divide-y divide-gray-100 dark:divide-gray-800">
            {documents.map((doc) => (
              <li key={doc.id} className="px-3 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <div className="flex items-start gap-2">
                  <FileText size={16} className="mt-0.5 text-blue-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{doc.filename}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mt-0.5">
                      {doc.description || doc.summary}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                      {doc.num_chunks} chunks &middot;{" "}
                      {(doc.size_bytes / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <div className="flex gap-1 flex-shrink-0">
                    <button
                      onClick={() => setPreview(doc)}
                      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                      title="Preview"
                    >
                      <Eye size={14} />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Preview modal */}
      {preview && (
        <PreviewModal doc={preview} onClose={() => setPreview(null)} />
      )}
    </div>
  );
}

function PreviewModal({ doc, onClose }: { doc: DocumentInfo; onClose: () => void }) {
  const fileUrl = getDocumentFileUrl(doc.id);
  const ext = doc.filename.split(".").pop()?.toLowerCase();
  const isText = ["txt", "md", "html", "json"].includes(ext || "");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-[90vw] max-w-3xl h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h2 className="font-semibold truncate">{doc.filename}</h2>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
          >
            <X size={18} />
          </button>
        </div>
        <div className="flex-1 overflow-hidden p-4">
          <div className="mb-3 text-sm text-gray-600 dark:text-gray-300">
            <strong>Summary:</strong> {doc.summary}
          </div>
          <div className="flex-1 border rounded-lg overflow-auto h-[calc(100%-4rem)]">
            {ext === "pdf" ? (
              <iframe
                src={fileUrl}
                className="w-full h-full"
                title={doc.filename}
              />
            ) : isText ? (
              <TextPreview url={fileUrl} />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <a
                  href={fileUrl}
                  download
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Download {doc.filename}
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function TextPreview({ url }: { url: string }) {
  const [text, setText] = useState<string>("Loading...");

  useEffect(() => {
    fetch(url)
      .then((r) => r.text())
      .then(setText)
      .catch(() => setText("Failed to load preview"));
  }, [url]);

  return (
    <pre className="p-4 text-sm whitespace-pre-wrap font-mono bg-gray-50 dark:bg-gray-900 h-full overflow-auto">
      {text}
    </pre>
  );
}
