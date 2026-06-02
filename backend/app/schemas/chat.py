from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ChatCreateRequest(BaseModel):
    title: Optional[str] = "Yeni Sohbet"
    model: Optional[str] = "gpt-4o"
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096


class ChatUpdateRequest(BaseModel):
    title: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatResponse(BaseModel):
    id: str
    title: str
    model: str
    system_prompt: Optional[str] = None
    temperature: float
    max_tokens: int
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    chats: list[ChatResponse]
    total: int


class MessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    metadata: Optional[Any] = None
    tokens_used: int
    model: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    use_memory: Optional[bool] = True
    use_rag: Optional[bool] = False
    use_web_search: Optional[bool] = False
    document_ids: Optional[list[str]] = None
    tool_ids: Optional[list[str]] = None
