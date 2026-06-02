"use client";
import { useRouter } from "next/navigation";
import { useChatStore } from "@/store/chat";
import { ChatInput } from "@/components/chat/chat-input";
import { ArrowRight } from "lucide-react";

const suggestions = [
  "Bana Osmanlı İmparatorluğu'nun yükselişini anlat",
  "İznik çinisinin sırlarını açıkla",
  "Divan edebiyatından bir beyit yaz",
  "Mevlana'nın hayatı ve öğretilerini özetle",
];

export default function HomePage() {
  const router = useRouter();
  const { createAndSendMessage } = useChatStore();

  const handleSend = async (content: string) => {
    const chat = await createAndSendMessage(content);
    if (chat) {
      router.push(`/c/${chat.id}`);
    }
  };

  const handleSuggestion = (suggestion: string) => {
    handleSend(suggestion);
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex-1 flex flex-col items-center justify-center px-4">
          <div className="max-w-2xl w-full text-center mb-12">
            <img src="/images/logo.png" alt="Osmanlı Yapay Zeka" className="h-20 w-20 mx-auto mb-6" />
          <h1 className="text-4xl font-bold mb-3 font-ottoman">Size nasıl yardımcı olabilirim?</h1>
          <p className="text-muted-foreground font-ottoman text-lg">
            Osmanlı zarafetinde, yapay zeka gücünde
          </p>
        </div>

        <div className="w-full max-w-2xl mb-8">
          <ChatInput onSend={handleSend} isStreaming={false} />
        </div>

        <div className="grid grid-cols-2 gap-3 max-w-2xl w-full">
          {suggestions.map((suggestion, i) => (
            <button
              key={i}
              onClick={() => handleSuggestion(suggestion)}
              className="flex items-center gap-2 text-left p-4 rounded-xl border border-border hover:border-primary/30 hover:bg-secondary/50 transition-all text-sm group"
            >
              <span className="flex-1 text-muted-foreground group-hover:text-foreground transition-colors leading-relaxed">
                {suggestion}
              </span>
              <ArrowRight size={14} className="text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
