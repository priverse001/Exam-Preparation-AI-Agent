import { ChatKit, useChatKit } from "@openai/chatkit-react";

interface ChatPanelProps {
  theme: "light" | "dark";
}

export function ChatPanel({ theme }: ChatPanelProps) {
  const chatkit = useChatKit({
    // >>> EXERCISE_9_START
    api: {
      url: "/exam-assistant/chatkit",
      domainKey: "domain_pk_localhost_dev",
    },
    theme: {
      colorScheme: theme,
    },
    startScreen: {
      greeting: "Welcome to your AI Study Assistant!",
      prompts: [
        {
          label: "Summarize my documents",
          prompt: "Summarize all my uploaded documents",
          icon: "sparkle",
        },
        {
          label: "Explain a concept",
          prompt: "Explain the key concepts from my notes",
          icon: "notebook",
        },
        {
          label: "Create revision notes",
          prompt: "Create revision notes for my exam topics and save them as markdown",
          icon: "chart",
        },
      ],
    },
    header: {
      title: { text: "Study Assistant" },
    },
    composer: {
      placeholder: "Ask about your study materials...",
    },
    disclaimer: {
      text: "Answers are grounded in your uploaded materials. Always verify important information.",
    },
    threadItemActions: {
      feedback: false,
      retry: true,
    },
    onError: ({ error }) => {
      console.error("ChatKit error:", error);
    },
    // >>> EXERCISE_9_END
  });

  return (
    <ChatKit
      control={chatkit.control}
      className="block h-full w-full"
      style={{ border: "none" }}
    />
  );
}
