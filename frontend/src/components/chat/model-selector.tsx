"use client";
import { useState, useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AIModel } from "@/types";
import { api } from "@/lib/api";
import { Brain } from "lucide-react";

interface ModelSelectorProps {
  currentModel: string;
  onModelChange: (model: string) => void;
}

const fallbackModels: AIModel[] = [
  { id: "gpt-4o", name: "GPT-4o", provider: "OpenAI", description: "", supports_tools: true, supports_streaming: true },
  { id: "gpt-4o-mini", name: "GPT-4o Mini", provider: "OpenAI", description: "", supports_tools: true, supports_streaming: true },
  { id: "claude-3-5-sonnet-20241022", name: "Claude 3.5 Sonnet", provider: "Anthropic", description: "", supports_tools: true, supports_streaming: true },
  { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro", provider: "Google", description: "", supports_tools: false, supports_streaming: true },
  { id: "ollama/llama3.1", name: "Llama 3.1 (Local)", provider: "Ollama", description: "", supports_tools: false, supports_streaming: true },
];

export function ModelSelector({ currentModel, onModelChange }: ModelSelectorProps) {
  const [models, setModels] = useState<AIModel[]>(fallbackModels);

  useEffect(() => {
    api.get<{ models: AIModel[] }>("/models")
      .then((data) => setModels(data.models))
      .catch(() => {});
  }, []);

  return (
    <Select value={currentModel} onValueChange={onModelChange}>
      <SelectTrigger className="w-[200px] h-8 text-xs border-0 bg-secondary/50 hover:bg-secondary">
        <Brain size={14} className="mr-1" />
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {models.map((model) => (
          <SelectItem key={model.id} value={model.id}>
            <div className="flex flex-col">
              <span>{model.name}</span>
              <span className="text-xs text-muted-foreground">{model.provider}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
