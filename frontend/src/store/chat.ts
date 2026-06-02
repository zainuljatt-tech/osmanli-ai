"use client";
import { create } from "zustand";
import { Chat, Message, StreamChunk } from "@/types";
import { api, streamChat } from "@/lib/api";

interface ChatState {
  chats: Chat[];
  currentChat: Chat | null;
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  isLoadingChats: boolean;
  isLoadingMessages: boolean;

  fetchChats: () => Promise<void>;
  createChat: () => Promise<Chat | null>;
  selectChat: (chatId: string) => Promise<void>;
  deleteChat: (chatId: string) => Promise<void>;
  renameChat: (chatId: string, title: string) => Promise<void>;
  sendMessage: (content: string, options?: Record<string, unknown>) => Promise<void>;
  createAndSendMessage: (content: string) => Promise<Chat | null>;
  appendChunk: (chunk: StreamChunk) => void;
  clearStreaming: () => void;
  updateChatModel: (chatId: string, model: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  currentChat: null,
  messages: [],
  isStreaming: false,
  streamingContent: "",
  isLoadingChats: false,
  isLoadingMessages: false,

  fetchChats: async () => {
    set({ isLoadingChats: true });
    try {
      const data = await api.get<{ chats: Chat[]; total: number }>("/chat");
      set({ chats: data.chats, isLoadingChats: false });
    } catch {
      set({ isLoadingChats: false });
    }
  },

  createChat: async () => {
    try {
      const chat = await api.post<Chat>("/chat", { title: "Yeni Sohbet" });
      set((state) => ({ chats: [chat, ...state.chats] }));
      return chat;
    } catch {
      return null;
    }
  },

  selectChat: async (chatId: string) => {
    set({ isLoadingMessages: true, currentChat: null });
    try {
      const data = await api.get<{
        id: string;
        title: string;
        model: string;
        system_prompt: string | null;
        temperature: number;
        max_tokens: number;
        message_count: number;
        messages: Message[];
        created_at: string;
        updated_at: string;
      }>(`/chat/${chatId}`);

      set({
        currentChat: {
          id: data.id,
          title: data.title,
          model: data.model,
          system_prompt: data.system_prompt,
          temperature: data.temperature,
          max_tokens: data.max_tokens,
          message_count: data.message_count,
          created_at: data.created_at,
          updated_at: data.updated_at,
        },
        messages: data.messages,
        isLoadingMessages: false,
      });
    } catch {
      set({ isLoadingMessages: false });
    }
  },

  createAndSendMessage: async (content: string) => {
    try {
      const chat = await api.post<Chat>("/chat", { title: "Yeni Sohbet" });
      set((state) => ({
        chats: [chat, ...state.chats],
        currentChat: chat,
        messages: [],
      }));
      get().sendMessage(content);
      return chat;
    } catch {
      return null;
    }
  },

  deleteChat: async (chatId: string) => {
    await api.delete(`/chat/${chatId}`);
    set((state) => ({
      chats: state.chats.filter((c) => c.id !== chatId),
      currentChat: state.currentChat?.id === chatId ? null : state.currentChat,
      messages: state.currentChat?.id === chatId ? [] : state.messages,
    }));
  },

  renameChat: async (chatId: string, title: string) => {
    await api.patch(`/chat/${chatId}`, { title });
    set((state) => ({
      chats: state.chats.map((c) =>
        c.id === chatId ? { ...c, title } : c
      ),
      currentChat:
        state.currentChat?.id === chatId
          ? { ...state.currentChat, title }
          : state.currentChat,
    }));
  },

  sendMessage: async (content, options = {}) => {
    const state = get();
    const chat = state.currentChat;
    if (!chat) return;

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      chat_id: chat.id,
      role: "user",
      content,
      metadata: null,
      tokens_used: 0,
      model: null,
      created_at: new Date().toISOString(),
    };

    set((s) => ({
      messages: [...s.messages, userMessage],
      isStreaming: true,
      streamingContent: "",
    }));

    let fullContent = "";
    let hasError = false;

    await streamChat(
      chat.id,
      {
        content,
        model: chat.model,
        temperature: chat.temperature,
        max_tokens: chat.max_tokens,
        system_prompt: chat.system_prompt,
        ...options,
      },
      (chunk) => {
        if (chunk.type === "content") {
          fullContent += (chunk.content as string) || "";
          set({ streamingContent: fullContent });
        }
      },
      (error) => {
        hasError = true;
        console.error(error);
      }
    );

    if (hasError) {
      set({ isStreaming: false, streamingContent: "" });
      return;
    }

    if (fullContent) {
      const assistantMessage: Message = {
        id: `temp-${Date.now()}-ai`,
        chat_id: chat.id,
        role: "assistant",
        content: fullContent,
        metadata: null,
        tokens_used: 0,
        model: chat.model,
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isStreaming: false,
        streamingContent: "",
      }));

      if (chat.title === "Yeni Sohbet") {
        get().fetchChats();
      }
    } else {
      set({ isStreaming: false, streamingContent: "" });
    }
  },

  appendChunk: (chunk) => {
    if (chunk.type === "content") {
      set((state) => ({
        streamingContent: state.streamingContent + (chunk.content || ""),
      }));
    }
  },

  clearStreaming: () => {
    set({ isStreaming: false, streamingContent: "" });
  },

  updateChatModel: async (chatId: string, model: string) => {
    await api.patch(`/chat/${chatId}`, { model });
    set((state) => ({
      chats: state.chats.map((c) =>
        c.id === chatId ? { ...c, model } : c
      ),
      currentChat:
        state.currentChat?.id === chatId
          ? { ...state.currentChat, model }
          : state.currentChat,
    }));
  },
}));
