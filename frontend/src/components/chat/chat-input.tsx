"use client";
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Send, Paperclip, Mic, StopCircle } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isStreaming: boolean;
  onStop?: () => void;
  onFileUpload?: () => void;
}

export function ChatInput({ onSend, isStreaming, onStop, onFileUpload }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [input]);

  useEffect(() => {
    if (!isStreaming && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isStreaming]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-border bg-background">
      <div className="max-w-4xl mx-auto px-2 py-2 md:px-4 md:py-3">
        <div className="relative flex items-end gap-1 md:gap-2 bg-secondary/50 rounded-2xl border border-border px-3 py-2 md:px-4 md:py-3 focus-within:ring-1 focus-within:ring-ring transition-all">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Mesaj yaz..."
            rows={1}
            className="flex-1 bg-transparent resize-none outline-none text-base md:text-sm leading-relaxed max-h-[120px] md:max-h-[200px] placeholder:text-muted-foreground min-h-[24px]"
            disabled={isStreaming}
          />

          <div className="flex items-center gap-1 shrink-0">
            {onFileUpload && (
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9 md:h-8 md:w-8 rounded-full"
                onClick={onFileUpload}
                disabled={isStreaming}
              >
                <Paperclip size={18} />
              </Button>
            )}

            {isStreaming ? (
              <Button
                variant="destructive"
                size="icon"
                className="h-9 w-9 md:h-8 md:w-8 rounded-full"
                onClick={onStop}
              >
                <StopCircle size={18} />
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={!input.trim()}
                size="icon"
                className="h-9 w-9 md:h-8 md:w-8 rounded-full"
              >
                <Send size={18} />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
