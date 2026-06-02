from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.types import get_uuid_type, make_uuid
import enum


class UserRole(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(get_uuid_type(), primary_key=True, default=make_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.FREE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    api_key = Column(String(255), unique=True, nullable=True)
    total_messages = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("UserUsage", back_populates="user", cascade="all, delete-orphan")


class UserUsage(Base):
    __tablename__ = "user_usage"

    id = Column(get_uuid_type(), primary_key=True, default=make_uuid)
    user_id = Column(get_uuid_type(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    messages_count = Column(Integer, default=0, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    storage_bytes = Column(Integer, default=0, nullable=False)
    voice_seconds = Column(Integer, default=0, nullable=False)
    search_queries = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="usage_records")
