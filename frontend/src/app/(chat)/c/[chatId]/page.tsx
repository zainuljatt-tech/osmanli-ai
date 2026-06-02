"use client";
import { useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import { useChatStore } from "@/store/chat";
import { MessageBubble } from "@/components/chat/message";
import { ChatInput } from "@/components/chat/chat-input";
import { ModelSelector } from "@/components/chat/model-selector";
import { Button } from "@/components/ui/button";
import { Edit2, Check, X } from "lucide-react";
import { useState } from "react";

export default function ChatPage() {
  const params = useParams();
  const chatId = params.chatId as string;
  const {
    currentChat,
    messages,
    isStreaming,
    streamingContent,
    isLoadingMessages,
    selectChat,
    sendMessage,
    clearStreaming,
    renameChat,
  } = useChatStore();

  const [editingTitle, setEditingTitle] = useState(false);
  const [titleInput, setTitleInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatId) {
      selectChat(chatId);
    }
  }, [chatId, selectChat]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const handleSend = (content: string) => {
    sendMessage(content);
  };

  const handleStop = () => {
    clearStreaming();
  };

  const handleRename = async () => {
    if (titleInput.trim() && currentChat) {
      await renameChat(currentChat.id, titleInput.trim());
    }
    setEditingTitle(false);
  };

  if (isLoadingMessages) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="flex gap-1">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <div className="flex items-center justify-between px-4 py-2 border-b border-border">
        <div className="flex items-center gap-2">
          {editingTitle ? (
            <div className="flex items-center gap-1">
              <input
                value={titleInput}
                onChange={(e) => setTitleInput(e.target.value)}
                className="h-7 px-2 rounded border border-input bg-background text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleRename();
                  if (e.key === "Escape") setEditingTitle(false);
                }}
              />
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleRename}>
                <Check size={14} />
              </Button>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setEditingTitle(false)}>
                <X size={14} />
              </Button>
            </div>
          ) : (
            <>
              <img src="/images/logo.png" alt="" className="h-5 w-5" />
              <h1 className="text-sm font-medium truncate max-w-[300px]">
                {currentChat?.title || "Sohbet"}
              </h1>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => {
                  setTitleInput(currentChat?.title || "");
                  setEditingTitle(true);
                }}
              >
                <Edit2 size={12} />
              </Button>
            </>
          )}
        </div>

        {currentChat && (
          <ModelSelector
            currentModel={currentChat.model}
            onModelChange={(model) => {
              useChatStore.getState().updateChatModel(chatId, model);
            }}
          />
        )}
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin min-h-0">
        <div className="max-w-4xl mx-auto px-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-20">
              <img src="/images/logo.png" alt="" className="h-20 w-20 mb-4" />
              <p className="text-muted-foreground text-sm">
                Bir mesaj göndererek sohbeti başlatın
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}

              {isStreaming && streamingContent && (
                <MessageBubble
                  message={{
                    id: "streaming",
                    chat_id: chatId,
                    role: "assistant",
                    content: streamingContent,
                    metadata: null,
                    tokens_used: 0,
                    model: null,
                    created_at: new Date().toISOString(),
                  }}
                  isStreaming
                />
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <ChatInput
        onSend={handleSend}
        isStreaming={isStreaming}
        onStop={handleStop}
      />
    </div>
  );
}
