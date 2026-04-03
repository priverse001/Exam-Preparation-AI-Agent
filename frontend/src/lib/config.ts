import { StartScreenPrompt } from "@openai/chatkit";

export const THEME_STORAGE_KEY = "exam-prep-assistant-theme";

const EXAM_PREP_API_BASE =
  import.meta.env.VITE_EXAM_PREP_API_BASE ??
  import.meta.env.VITE_KNOWLEDGE_API_BASE ?? "/exam-assistant";

export const EXAM_PREP_CHATKIT_API_URL =
  import.meta.env.VITE_EXAM_PREP_CHATKIT_API_URL ??
  import.meta.env.VITE_KNOWLEDGE_CHATKIT_API_URL ??
  `${EXAM_PREP_API_BASE}/chatkit`;

/**
 * ChatKit still expects a domain key at runtime. Use any placeholder locally,
 * but register your production domain at
 * https://platform.openai.com/settings/organization/security/domain-allowlist
 * and deploy the real key.
 */
export const EXAM_PREP_CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_EXAM_PREP_CHATKIT_API_DOMAIN_KEY ??
  import.meta.env.VITE_EXAM_PREP_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const EXAM_PREP_DOCUMENTS_URL =
  import.meta.env.VITE_EXAM_PREP_DOCUMENTS_URL ??
  import.meta.env.VITE_KNOWLEDGE_DOCUMENTS_URL ??
  `${EXAM_PREP_API_BASE}/documents`;

export const EXAM_PREP_DOCUMENT_FILE_URL = (documentId: string): string =>
  `${
    import.meta.env.VITE_EXAM_PREP_DOCUMENT_FILE_BASE_URL ??
    import.meta.env.VITE_KNOWLEDGE_DOCUMENT_FILE_BASE_URL ??
    `${EXAM_PREP_API_BASE}/documents`
  }/${documentId}/file`;


export const EXAM_PREP_GREETING =
  import.meta.env.VITE_EXAM_PREP_GREETING ??
  import.meta.env.VITE_KNOWLEDGE_GREETING ??
  "Welcome to your AI course-material copilot";

export const EXAM_PREP_STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Summarize notes",
    prompt: "Summarize the most important ideas from my uploaded notes.",
    icon: "sparkle",
  },
  {
    label: "Ask a concept question",
    prompt: "Explain the main idea from my uploaded material with citations.",
    icon: "chart",
  },
  {
    label: "Create revision notes",
    prompt: "Create a markdown revision sheet from my uploaded material and save it.",
    icon: "notebook",
  },
];

export const EXAM_PREP_COMPOSER_PLACEHOLDER =
  import.meta.env.VITE_EXAM_PREP_COMPOSER_PLACEHOLDER ??
  import.meta.env.VITE_KNOWLEDGE_COMPOSER_PLACEHOLDER ??
  "Ask about uploaded notes or ask the agent to save revision notes";
