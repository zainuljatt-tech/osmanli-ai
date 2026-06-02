from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.types import get_uuid_type, make_uuid
from sqlalchemy.dialects.postgresql import JSONB


class Chat(Base):
    __tablename__ = "chats"

    id = Column(get_uuid_type(), primary_key=True, default=make_uuid)
    user_id = Column(get_uuid_type(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="Yeni Sohbet", nullable=False)
    model = Column(String(50), default="gpt-4o", nullable=False)
    system_prompt = Column(Text, nullable=True)
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, default=4096, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(get_uuid_type(), primary_key=True, default=make_uuid)
    chat_id = Column(get_uuid_type(), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    msg_metadata = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0, nullable=False)
    model = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    chat = relationship("Chat", back_populates="messages")
