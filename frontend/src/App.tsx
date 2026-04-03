import { useState, useEffect, useCallback } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentPanel } from "./components/DocumentPanel";
import { DocumentInfo, fetchDocuments } from "./api";
import { Moon, Sun } from "lucide-react";

export default function App() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [dark, setDark] = useState(false);

  const refreshDocuments = useCallback(async () => {
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
    } catch (e) {
      console.error("Failed to load documents:", e);
    }
  }, []);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <div className="flex h-screen w-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Left: Documents Panel */}
      <div className="w-80 flex-shrink-0 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-lg font-bold">Study Assistant</h1>
          <button
            onClick={() => setDark(!dark)}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
            title="Toggle theme"
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
        <DocumentPanel
          documents={documents}
          onRefresh={refreshDocuments}
        />
      </div>

      {/* Right: Chat Panel */}
      <div className="flex-1 flex flex-col min-w-0">
        <ChatPanel theme={dark ? "dark" : "light"} />
      </div>
    </div>
  );
}
