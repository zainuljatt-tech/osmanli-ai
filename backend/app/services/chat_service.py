from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.models.chat import Chat, Message
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime, timezone


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_chat(self, user_id: str, title: str = "Yeni Sohbet", model: str = "gpt-4o",
                    system_prompt: Optional[str] = None, temperature: float = 0.7,
                    max_tokens: int = 4096) -> Chat:
        chat = Chat(
            user_id=user_id, title=title, model=model,
            system_prompt=system_prompt, temperature=temperature, max_tokens=max_tokens,
        )
        self.db.add(chat)
        self.db.flush()
        return chat

    def get_user_chats(self, user_id: str, limit: int = 50, offset: int = 0) -> tuple[list[Chat], int]:
        total = self.db.scalar(
            select(func.count(Chat.id)).where(Chat.user_id == user_id, Chat.is_archived == False)
        ) or 0
        result = self.db.execute(
            select(Chat).where(Chat.user_id == user_id, Chat.is_archived == False)
            .order_by(desc(Chat.updated_at)).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    def get_chat(self, chat_id: str, user_id: str) -> Chat:
        result = self.db.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
        return chat

    def update_chat(self, chat_id: str, user_id: str, **kwargs) -> Chat:
        chat = self.get_chat(chat_id, user_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(chat, key):
                setattr(chat, key, value)
        chat.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return chat

    def delete_chat(self, chat_id: str, user_id: str):
        chat = self.get_chat(chat_id, user_id)
        self.db.delete(chat)
        self.db.flush()

    def get_chat_messages(self, chat_id: str, user_id: str, limit: int = 100, offset: int = 0) -> list[Message]:
        self.get_chat(chat_id, user_id)
        result = self.db.execute(
            select(Message).where(Message.chat_id == chat_id)
            .order_by(Message.created_at).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    def save_message(self, chat_id: str, role: str, content: str,
                     model: Optional[str] = None, tokens_used: int = 0,
                     msg_metadata: Optional[dict] = None) -> Message:
        msg = Message(
            chat_id=chat_id, role=role, content=content,
            model=model, tokens_used=tokens_used, msg_metadata=msg_metadata,
        )
        self.db.add(msg)
        result = self.db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if chat:
            chat.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return msg


def get_chat_service(db: Session) -> ChatService:
    return ChatService(db)
