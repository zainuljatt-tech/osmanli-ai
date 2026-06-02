export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: "free" | "pro" | "enterprise" | "admin";
  is_verified: boolean;
  total_messages: number;
  created_at: string;
}

export interface Chat {
  id: string;
  title: string;
  model: string;
  system_prompt: string | null;
  temperature: number;
  max_tokens: number;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  chat_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  metadata: Record<string, unknown> | null;
  tokens_used: number;
  model: string | null;
  created_at: string;
}

export interface Memory {
  id: string;
  type: string;
  key: string | null;
  content: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface Document_ {
  id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: "processing" | "ready" | "failed";
  page_count: number | null;
  chunk_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface SearchResult {
  chunk_id: string;
  document_id: string;
  content: string;
  score: number;
  chunk_index: number;
  filename: string;
}

export interface Subscription {
  id?: string;
  plan: string;
  status: string;
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  created_at?: string;
}

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  supports_tools: boolean;
  supports_streaming: boolean;
}

export interface StreamChunk {
  type: "content" | "tool_call" | "tool_result" | "status" | "error";
  content?: string;
  tool_calls?: Array<{ id: string; function: { name: string; arguments: string } }>;
  tool_result?: Record<string, unknown>;
  name?: string;
  result?: Record<string, unknown>;
  error?: string;
}
